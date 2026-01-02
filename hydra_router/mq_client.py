"""
MQClient - Generic ZeroMQ client library for the Hydra Router system.

This module provides a unified interface for both client and server applications
to communicate with the Hydra Router, handling automatic message format conversion,
connection management, and comprehensive error handling.
"""

import asyncio
import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

import zmq
import zmq.asyncio

from .constants.DHydraLog import DHydraLog
from .constants.DMsgType import DMsgType
from .constants.DRouter import DRouter
from .exceptions import (
    ConnectionError,
    MessageFormatError,
    MessageValidationError,
    create_connection_error,
    create_timeout_error,
)
from .util.HydraLog import HydraLog
from .validation import MessageValidator


@dataclass
class ZMQMessage:
    """
    Internal message format used by client applications.

    This format is used internally by applications and is automatically
    converted to/from DRouter format by the MQClient.
    """

    message_type: DMsgType
    timestamp: Optional[float] = None
    client_id: Optional[str] = None
    request_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Set default timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = time.time()


class MQClient:
    """
    Generic ZeroMQ client library for communicating with the Hydra Router.

    Provides a unified interface for both client and server applications with:
    - Automatic message format conversion between ZMQMessage and DRouter
    - Connection lifecycle management including heartbeat sending
    - Both synchronous and asynchronous communication patterns
    - Comprehensive error handling and validation
    - Configurable client types and connection parameters
    """

    def __init__(
        self,
        router_address: str,
        client_type: str,
        heartbeat_interval: float = DRouter.HEARTBEAT_INTERVAL,
        client_id: Optional[str] = None,
        connection_timeout: float = DRouter.DEFAULT_CLIENT_TIMEOUT,
        message_timeout: float = DRouter.DEFAULT_MESSAGE_TIMEOUT,
    ):
        """
        Initialize the MQClient.

        Args:
            router_address: Address of the Hydra Router (e.g., "tcp://localhost:5556")
            client_type: Type of client (must be valid DRouter client type)
            heartbeat_interval: Interval between heartbeat messages in seconds
            client_id: Unique client identifier (auto-generated if None)
            connection_timeout: Timeout for connection operations in seconds
            message_timeout: Default timeout for message operations in seconds
        """
        self.router_address = router_address
        self.client_type = client_type
        self.heartbeat_interval = heartbeat_interval
        self.client_id = client_id or f"{client_type}-{uuid.uuid4().hex[:8]}"
        self.connection_timeout = connection_timeout
        self.message_timeout = message_timeout

        # Validation
        self.validator = MessageValidator()
        if not self.validator.validate_sender_type(client_type):
            valid_types = ", ".join(DRouter.VALID_CLIENT_TYPES)
            raise ValueError(
                f"Invalid client type '{client_type}', must be one of: {valid_types}"
            )

        # ZeroMQ components
        self.context: Optional[zmq.asyncio.Context] = None
        self.socket: Optional[zmq.asyncio.Socket] = None
        self.connected = False

        # Background tasks
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.receive_task: Optional[asyncio.Task] = None

        # Message handling
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.message_handlers: Dict[DMsgType, Callable] = {}

        # Logging
        self.logger = HydraLog(f"mq_client_{self.client_id}", to_console=True)
        self.logger.loglevel(DHydraLog.INFO)

        # Message type mapping
        self.message_type_mapping = self._create_message_type_mapping()

    def _create_message_type_mapping(self) -> Dict[str, str]:
        """Create mapping between DMsgType enum and DRouter."""
        return {
            DMsgType.HEARTBEAT.value: DRouter.HEARTBEAT,
            DMsgType.SQUARE_REQUEST.value: DRouter.SQUARE_REQUEST,
            DMsgType.SQUARE_RESPONSE.value: DRouter.SQUARE_RESPONSE,
            DMsgType.CLIENT_REGISTRY_REQUEST.value: DRouter.CLIENT_REGISTRY_REQUEST,
            DMsgType.CLIENT_REGISTRY_RESPONSE.value: DRouter.CLIENT_REGISTRY_RESPONSE,
            DMsgType.START_SIMULATION.value: DRouter.START_SIMULATION,
            DMsgType.STOP_SIMULATION.value: DRouter.STOP_SIMULATION,
            DMsgType.PAUSE_SIMULATION.value: DRouter.PAUSE_SIMULATION,
            DMsgType.RESUME_SIMULATION.value: DRouter.RESUME_SIMULATION,
            DMsgType.RESET_SIMULATION.value: DRouter.RESET_SIMULATION,
            DMsgType.GET_SIMULATION_STATUS.value: DRouter.GET_SIMULATION_STATUS,
            DMsgType.STATUS_UPDATE.value: DRouter.STATUS_UPDATE,
            DMsgType.SIMULATION_STARTED.value: DRouter.SIMULATION_STARTED,
            DMsgType.SIMULATION_STOPPED.value: DRouter.SIMULATION_STOPPED,
            DMsgType.SIMULATION_PAUSED.value: DRouter.SIMULATION_PAUSED,
            DMsgType.SIMULATION_RESUMED.value: DRouter.SIMULATION_RESUMED,
            DMsgType.SIMULATION_RESET.value: DRouter.SIMULATION_RESET,
            DMsgType.ERROR.value: DRouter.ERROR,
        }

    async def connect(self) -> bool:
        """
        Connect to the Hydra Router.

        Returns:
            True if connection successful, False otherwise

        Raises:
            ConnectionError: If connection fails
        """
        try:
            self.logger.info(f"Connecting to router at {self.router_address}")

            # Create ZeroMQ context and socket
            self.context = zmq.asyncio.Context()
            self.socket = self.context.socket(zmq.DEALER)
            self.socket.setsockopt(zmq.IDENTITY, self.client_id.encode())

            # Set socket options
            self.socket.setsockopt(zmq.LINGER, 1000)  # 1 second linger
            self.socket.setsockopt(zmq.RCVTIMEO, int(self.connection_timeout * 1000))
            self.socket.setsockopt(zmq.SNDTIMEO, int(self.connection_timeout * 1000))

            # Connect to router
            self.socket.connect(self.router_address)

            # Set connected flag
            self.connected = True

            # Start background tasks (heartbeat loop will send first heartbeat)
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            self.receive_task = asyncio.create_task(self._receive_loop())

            self.logger.info(
                f"Successfully connected to router as {self.client_type} ({self.client_id})"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to router: {e}")
            await self._cleanup_connection()
            raise create_connection_error(
                self.router_address.split("://")[1].split(":")[0],
                int(self.router_address.split(":")[-1]),
                e,
            )

    async def disconnect(self) -> None:
        """Disconnect from the Hydra Router and cleanup resources."""
        self.logger.info("Disconnecting from router")
        self.connected = False

        # Cancel background tasks
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass

        if self.receive_task:
            self.receive_task.cancel()
            try:
                await self.receive_task
            except asyncio.CancelledError:
                pass

        # Cancel pending requests
        for future in self.pending_requests.values():
            if not future.done():
                future.cancel()
        self.pending_requests.clear()

        await self._cleanup_connection()
        self.logger.info("Disconnected from router")

    async def _cleanup_connection(self) -> None:
        """Clean up ZeroMQ connection resources."""
        if self.socket:
            self.socket.close()
            self.socket = None

        if self.context:
            self.context.term()
            self.context = None

    async def send_message(self, message: ZMQMessage) -> None:
        """
        Send a message to the router.

        Args:
            message: The ZMQMessage to send

        Raises:
            ConnectionError: If not connected or send fails
            MessageFormatError: If message format conversion fails
        """
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected to router")

        try:
            # Convert to router format
            router_message = self._convert_to_router_format(message)

            # Validate the converted message
            is_valid, error = self.validator.validate_router_message(router_message)
            if not is_valid:
                raise MessageValidationError(f"Invalid router message format: {error}")

            # Debug: Log the message being sent
            self.logger.debug(f"SENDING MESSAGE: {message.message_type.value}")
            self.logger.debug(f"ROUTER FORMAT: {router_message}")

            # Send the message
            await self.socket.send_json(router_message)
            self.logger.debug(
                f"SUCCESSFULLY SENT: {message.message_type.value} -> {router_message}"
            )

        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            if isinstance(e, (MessageValidationError, MessageFormatError)):
                raise
            raise ConnectionError(f"Failed to send message: {e}")

    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """
        Receive a message from the router (non-blocking).

        Returns:
            Router message dictionary or None if no message available
        """
        if not self.connected or not self.socket:
            return None

        try:
            # Non-blocking receive
            message = await self.socket.recv_json(zmq.NOBLOCK)
            self.logger.debug(
                f"Received message: {message.get('elem', 'unknown')} -> {message}"
            )
            return message  # type: ignore[no-any-return]
        except zmq.Again:
            # No message available
            return None
        except Exception as e:
            self.logger.error(f"Failed to receive message: {e}")
            return None

    async def send_command(
        self,
        message_type: DMsgType,
        data: Dict[str, Any],
        timeout: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Send a command and wait for response with timeout.

        Args:
            message_type: Type of message to send
            data: Message data payload
            timeout: Timeout in seconds (uses default if None)

        Returns:
            Response message or None if timeout

        Raises:
            TimeoutError: If response not received within timeout
            ConnectionError: If send fails
        """
        if timeout is None:
            timeout = self.message_timeout

        # Generate request ID for correlation
        request_id = str(uuid.uuid4())

        # Create message
        message = ZMQMessage(
            message_type=message_type,
            timestamp=time.time(),
            client_id=self.client_id,
            request_id=request_id,
            data=data,
        )

        # Create future for response
        response_future: asyncio.Future[Dict[str, Any]] = asyncio.Future()
        self.pending_requests[request_id] = response_future

        try:
            # Send message
            await self.send_message(message)

            # Wait for response with timeout
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response

        except asyncio.TimeoutError:
            # Clean up pending request
            self.pending_requests.pop(request_id, None)
            raise create_timeout_error("send_command", timeout)
        except Exception:
            # Clean up pending request
            self.pending_requests.pop(request_id, None)
            raise

    async def request_client_registry(
        self, timeout: float = 5.0
    ) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Request client registry information from the router.

        Args:
            timeout: Timeout in seconds

        Returns:
            Client registry data or None if timeout/error
        """
        try:
            response = await self.send_command(
                DMsgType.CLIENT_REGISTRY_REQUEST, {}, timeout=timeout
            )

            if response and response.get("elem") == DRouter.CLIENT_REGISTRY_RESPONSE:
                return response.get("data", {})  # type: ignore[no-any-return]

            return None

        except Exception as e:
            self.logger.error(f"Failed to request client registry: {e}")
            return None

    def _convert_to_router_format(self, message: ZMQMessage) -> Dict[str, Any]:
        """
        Convert ZMQMessage to DRouter format.

        Args:
            message: ZMQMessage to convert

        Returns:
            DRouter format dictionary

        Raises:
            MessageFormatError: If conversion fails
        """
        try:
            # Map message type to router element
            elem = self._map_message_type_to_elem(message.message_type.value)

            router_message: Dict[str, Any] = {
                DRouter.SENDER: self.client_type,
                DRouter.ELEM: elem,
                DRouter.TIMESTAMP: message.timestamp,
            }

            # Add optional fields only if they have values
            if message.data is not None:
                router_message[DRouter.DATA] = message.data

            if message.client_id is not None:
                router_message[DRouter.CLIENT_ID] = message.client_id

            if message.request_id:
                router_message[DRouter.REQUEST_ID] = message.request_id

            return router_message

        except Exception as e:
            raise MessageFormatError(
                f"Failed to convert ZMQMessage to DRouter format: {e}",
                source_format="ZMQMessage",
                target_format="DRouter",
                conversion_step="message_type_mapping",
                original_message=message.__dict__,
            )

    def _convert_from_router_format(self, router_message: Dict[str, Any]) -> ZMQMessage:
        """
        Convert DRouter format to ZMQMessage.

        Args:
            router_message: DRouter format dictionary

        Returns:
            ZMQMessage instance

        Raises:
            MessageFormatError: If conversion fails
        """
        try:
            # Map router element to message type
            elem = router_message.get(DRouter.ELEM, "")
            message_type = self._map_elem_to_message_type(elem)

            return ZMQMessage(
                message_type=message_type,
                timestamp=router_message.get(DRouter.TIMESTAMP, time.time()),
                client_id=router_message.get(DRouter.CLIENT_ID),
                request_id=router_message.get(DRouter.REQUEST_ID),
                data=router_message.get(DRouter.DATA),
            )

        except Exception as e:
            raise MessageFormatError(
                f"Failed to convert DRouter to ZMQMessage format: {e}",
                source_format="DRouter",
                target_format="ZMQMessage",
                conversion_step="elem_to_message_type_mapping",
                original_message=router_message,
            )

    def _map_message_type_to_elem(self, message_type: str) -> str:
        """Map DMsgType to DRouter elem."""
        return self.message_type_mapping.get(message_type, message_type)

    def _map_elem_to_message_type(self, elem: str) -> DMsgType:
        """Map DRouter elem to DMsgType."""
        # Reverse lookup in mapping
        for msg_type, router_elem in self.message_type_mapping.items():
            if router_elem == elem:
                try:
                    return DMsgType(msg_type)
                except ValueError:
                    pass

        # If not found, try to create DMsgType directly
        try:
            return DMsgType(elem)
        except ValueError:
            # For completely unknown message types, raise an exception
            raise MessageFormatError(
                f"Unknown message type '{elem}' cannot be converted to DMsgType",
                source_format="DRouter",
                target_format="ZMQMessage",
                conversion_step="elem_to_message_type_mapping",
                original_message={"elem": elem},
            )

    def _validate_router_message(
        self, message: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate a DRouter format message."""
        return self.validator.validate_router_message(message)

    async def _send_heartbeat(self) -> None:
        """Send a heartbeat message to the router."""
        try:
            heartbeat_message = ZMQMessage(
                message_type=DMsgType.HEARTBEAT,
                timestamp=time.time(),
                client_id=self.client_id,
                data={"status": "alive"},
            )

            await self.send_message(heartbeat_message)
            self.logger.debug("Sent heartbeat")

        except Exception as e:
            self.logger.error(f"Failed to send heartbeat: {e}")

    async def _heartbeat_loop(self) -> None:
        """Background task for sending periodic heartbeats."""
        # Send immediate heartbeat on start
        try:
            if self.connected:
                await self._send_heartbeat()
        except Exception as e:
            self.logger.error(f"Initial heartbeat error: {e}")

        # Then send periodic heartbeats
        while self.connected:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                if self.connected:
                    await self._send_heartbeat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Heartbeat loop error: {e}")

    async def _receive_loop(self) -> None:
        """Background task for receiving and processing messages."""
        while self.connected:
            try:
                message = await self.receive_message()
                if message:
                    await self._process_received_message(message)
                else:
                    # Small delay to prevent busy waiting
                    await asyncio.sleep(0.01)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Receive loop error: {e}")

    async def _process_received_message(self, message: Dict[str, Any]) -> None:
        """Process a received message from the router."""
        try:
            # Check if this is a response to a pending request
            request_id = message.get(DRouter.REQUEST_ID)
            if request_id and request_id in self.pending_requests:
                future = self.pending_requests.pop(request_id)
                if not future.done():
                    future.set_result(message)
                return

            # Convert to ZMQMessage format
            zmq_message = self._convert_from_router_format(message)

            # Check for registered message handlers
            if zmq_message.message_type in self.message_handlers:
                handler = self.message_handlers[zmq_message.message_type]
                if asyncio.iscoroutinefunction(handler):
                    await handler(zmq_message)
                else:
                    handler(zmq_message)
            else:
                self.logger.debug(
                    f"No handler for message type: {zmq_message.message_type}"
                )

        except Exception as e:
            self.logger.error(f"Failed to process received message: {e}")

    def register_message_handler(
        self, message_type: DMsgType, handler: Callable
    ) -> None:
        """
        Register a handler for a specific message type.

        Args:
            message_type: The message type to handle
            handler: Function to call when message is received (can be async)
        """
        self.message_handlers[message_type] = handler
        self.logger.debug(f"Registered handler for {message_type}")

    def unregister_message_handler(self, message_type: DMsgType) -> None:
        """
        Unregister a message handler.

        Args:
            message_type: The message type to unregister
        """
        if message_type in self.message_handlers:
            del self.message_handlers[message_type]
            self.logger.debug(f"Unregistered handler for {message_type}")

    @property
    def is_connected(self) -> bool:
        """Check if client is connected to router."""
        return self.connected

    def get_client_info(self) -> Dict[str, Any]:
        """
        Get client information.

        Returns:
            Dictionary with client information
        """
        return {
            "client_id": self.client_id,
            "client_type": self.client_type,
            "router_address": self.router_address,
            "connected": self.connected,
            "heartbeat_interval": self.heartbeat_interval,
            "pending_requests": len(self.pending_requests),
            "registered_handlers": list(self.message_handlers.keys()),
        }

    async def __aenter__(self) -> "MQClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> bool:
        """Async context manager exit."""
        await self.disconnect()
        return False

    def _create_heartbeat_message(self) -> ZMQMessage:
        """Create a heartbeat message."""
        return ZMQMessage(message_type=DMsgType.HEARTBEAT, client_id=self.client_id)
