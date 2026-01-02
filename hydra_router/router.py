"""
HydraRouter - Central message routing component for the Hydra Router system.

This module provides the central router that manages client connections and routes
messages between multiple clients and a single server using ZeroMQ ROUTER socket.
"""

import asyncio
import logging
import signal
import time
from typing import Any, Dict, List, Optional, Tuple

import zmq
import zmq.asyncio

from .exceptions import ConnectionError, MessageRoutingError, ServerNotAvailableError
from .router_constants import RouterConstants
from .validation import MessageValidator


class ClientRegistry:
    """
    Thread-safe client registry for tracking connected clients and servers.

    Manages client connections, heartbeat timestamps, and provides
    efficient lookup and pruning operations.
    """

    def __init__(self) -> None:
        """Initialize the client registry."""
        self.clients: Dict[
            str, Tuple[str, float]
        ] = {}  # client_id -> (client_type, last_heartbeat)
        self.server_id: Optional[str] = None
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger("hydra_router.client_registry")

    async def register_client(self, client_id: str, client_type: str) -> None:
        """
        Register a new client.

        Args:
            client_id: Unique client identifier
            client_type: Type of client (must be valid DRouter type)
        """
        async with self.lock:
            self.clients[client_id] = (client_type, time.time())

            # Track server separately
            if client_type == DRouter.HYDRA_SERVER:
                if self.server_id and self.server_id != client_id:
                    self.logger.warning(
                        f"Replacing existing server {self.server_id} with {client_id}"
                    )
                self.server_id = client_id

            self.logger.info(f"Registered {client_type} client: {client_id}")

    async def update_heartbeat(self, client_id: str) -> None:
        """
        Update the heartbeat timestamp for a client.

        Args:
            client_id: Client identifier to update
        """
        async with self.lock:
            if client_id in self.clients:
                client_type, _ = self.clients[client_id]
                self.clients[client_id] = (client_type, time.time())
                self.logger.debug(f"Updated heartbeat for {client_id}")

    async def remove_client(self, client_id: str) -> None:
        """
        Remove a client from the registry.

        Args:
            client_id: Client identifier to remove
        """
        async with self.lock:
            if client_id in self.clients:
                client_type, _ = self.clients[client_id]
                del self.clients[client_id]

                # Clear server reference if this was the server
                if client_id == self.server_id:
                    self.server_id = None
                    self.logger.info(f"Server {client_id} disconnected")

                self.logger.info(f"Removed {client_type} client: {client_id}")

    async def get_clients_by_type(self, client_type: str) -> List[str]:
        """
        Get all clients of a specific type.

        Args:
            client_type: Type of clients to retrieve

        Returns:
            List of client IDs matching the type
        """
        async with self.lock:
            return [
                client_id
                for client_id, (ctype, _) in self.clients.items()
                if ctype == client_type
            ]

    async def prune_inactive_clients(self, timeout: float) -> List[str]:
        """
        Remove clients that haven't sent heartbeats within timeout.

        Args:
            timeout: Timeout in seconds

        Returns:
            List of removed client IDs
        """
        current_time = time.time()
        removed_clients = []

        async with self.lock:
            inactive_clients = [
                client_id
                for client_id, (_, last_heartbeat) in self.clients.items()
                if current_time - last_heartbeat > timeout
            ]

            for client_id in inactive_clients:
                client_type, _ = self.clients[client_id]
                del self.clients[client_id]
                removed_clients.append(client_id)

                # Clear server reference if this was the server
                if client_id == self.server_id:
                    self.server_id = None
                    self.logger.info(f"Server {client_id} timed out")

                self.logger.info(f"Pruned inactive {client_type} client: {client_id}")

        return removed_clients

    async def get_registry_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Get complete registry data for client registry queries.

        Returns:
            Dictionary with client information
        """
        async with self.lock:
            registry_data = {}
            for client_id, (client_type, last_heartbeat) in self.clients.items():
                registry_data[client_id] = {
                    "client_type": client_type,
                    "last_heartbeat": last_heartbeat,
                    "is_server": client_id == self.server_id,
                }
            return registry_data

    async def has_server(self) -> bool:
        """Check if a server is currently connected."""
        async with self.lock:
            return self.server_id is not None and self.server_id in self.clients

    async def get_client_count(self) -> int:
        """Get total number of connected clients."""
        async with self.lock:
            return len(self.clients)


class MessageRouter:
    """
    Message routing logic for the Hydra Router.

    Handles routing messages between clients and servers based on
    sender type and routing rules.
    """

    def __init__(self, client_registry: ClientRegistry, socket: zmq.asyncio.Socket):
        """
        Initialize the message router.

        Args:
            client_registry: Client registry instance
            socket: ZeroMQ ROUTER socket for sending messages
        """
        self.client_registry = client_registry
        self.socket = socket
        self.logger = logging.getLogger("hydra_router.message_router")

    async def route_message(self, sender_id: str, message: Dict[str, Any]) -> None:
        """
        Route a message based on sender type and routing rules.

        Args:
            sender_id: ID of the client that sent the message
            message: The message to route
        """
        sender_type = message.get(DRouter.SENDER)
        elem = message.get(DRouter.ELEM)

        self.logger.debug(f"Routing message from {sender_id} ({sender_type}): {elem}")

        # Handle different routing scenarios
        if sender_type == DRouter.HYDRA_CLIENT or sender_type == DRouter.SIMPLE_CLIENT:
            await self._route_client_message(sender_id, message)
        elif (
            sender_type == DRouter.HYDRA_SERVER or sender_type == DRouter.SIMPLE_SERVER
        ):
            await self._route_server_message(sender_id, message)
        else:
            self.logger.warning(f"Unknown sender type for routing: {sender_type}")

    async def _route_client_message(
        self, sender_id: str, message: Dict[str, Any]
    ) -> None:
        """Route a message from a client."""
        elem = message.get(DRouter.ELEM)

        # Handle client registry requests
        if elem == DRouter.CLIENT_REGISTRY_REQUEST:
            await self._handle_client_registry_request(sender_id, message)
            return

        # Handle heartbeat messages (no forwarding needed)
        if elem == DRouter.HEARTBEAT:
            await self.client_registry.update_heartbeat(sender_id)
            return

        # Forward other client messages to server
        if await self.client_registry.has_server():
            await self._forward_to_server(message)
        else:
            await self._send_no_server_error(sender_id, message)

    async def _route_server_message(
        self, sender_id: str, message: Dict[str, Any]
    ) -> None:
        """Route a message from a server."""
        elem = message.get(DRouter.ELEM)

        # Handle heartbeat messages (no forwarding needed)
        if elem == DRouter.HEARTBEAT:
            await self.client_registry.update_heartbeat(sender_id)
            return

        # Broadcast server messages to all clients (except the server itself)
        await self._broadcast_to_clients(message, exclude_sender=sender_id)

    async def _forward_to_server(self, message: Dict[str, Any]) -> None:
        """Forward a message to the connected server."""
        if not await self.client_registry.has_server():
            raise ServerNotAvailableError("No server available for message forwarding")

        server_id = self.client_registry.server_id
        if server_id:
            try:
                await self.socket.send_multipart(
                    [server_id.encode(), zmq.utils.jsonapi.dumps(message)]
                )
                self.logger.debug(f"Forwarded message to server {server_id}")
            except Exception as e:
                self.logger.error(f"Failed to forward message to server: {e}")
                raise MessageRoutingError(
                    f"Failed to forward message to server {server_id}",
                    target_client=server_id,
                    message_type=message.get(DRouter.ELEM),
                )

    async def _broadcast_to_clients(
        self, message: Dict[str, Any], exclude_sender: Optional[str] = None
    ) -> None:
        """Broadcast a message to all connected clients."""
        registry_data = await self.client_registry.get_registry_data()

        for client_id, client_info in registry_data.items():
            # Skip the sender and servers
            if client_id == exclude_sender:
                continue
            if client_info["client_type"] in [
                DRouter.HYDRA_SERVER,
                DRouter.SIMPLE_SERVER,
            ]:
                continue

            try:
                await self.socket.send_multipart(
                    [client_id.encode(), zmq.utils.jsonapi.dumps(message)]
                )
                self.logger.debug(f"Broadcast message to client {client_id}")
            except Exception as e:
                self.logger.error(f"Failed to broadcast to client {client_id}: {e}")

    async def _handle_client_registry_request(
        self, sender_id: str, message: Dict[str, Any]
    ) -> None:
        """Handle a client registry request."""
        try:
            registry_data = await self.client_registry.get_registry_data()

            response = {
                DRouter.SENDER: DRouter.HYDRA_ROUTER,
                DRouter.ELEM: DRouter.CLIENT_REGISTRY_RESPONSE,
                DRouter.DATA: registry_data,
                DRouter.CLIENT_ID: DRouter.HYDRA_ROUTER,
                DRouter.TIMESTAMP: time.time(),
                DRouter.REQUEST_ID: message.get(DRouter.REQUEST_ID),
            }

            await self.socket.send_multipart(
                [sender_id.encode(), zmq.utils.jsonapi.dumps(response)]
            )

            self.logger.debug(f"Sent client registry response to {sender_id}")

        except Exception as e:
            self.logger.error(f"Failed to handle client registry request: {e}")

    async def _send_no_server_error(
        self, sender_id: str, message: Dict[str, Any]
    ) -> None:
        """Send a 'no server connected' error response to a client."""
        error_response = {
            DRouter.SENDER: DRouter.HYDRA_ROUTER,
            DRouter.ELEM: DRouter.ERROR,
            DRouter.DATA: {
                "error": DRouter.NO_SERVER_CONNECTED,
                "message": "No server connected to handle client request",
                "original_request": message.get(DRouter.ELEM),
            },
            DRouter.CLIENT_ID: DRouter.HYDRA_ROUTER,
            DRouter.TIMESTAMP: time.time(),
            DRouter.REQUEST_ID: message.get(DRouter.REQUEST_ID),
        }

        try:
            await self.socket.send_multipart(
                [sender_id.encode(), zmq.utils.jsonapi.dumps(error_response)]
            )
            self.logger.debug(f"Sent no-server error to {sender_id}")
        except Exception as e:
            self.logger.error(f"Failed to send no-server error: {e}")


class HydraRouter:
    """
    Central message routing component for the Hydra Router system.

    Manages client connections and routes messages between multiple clients
    and a single server using ZeroMQ ROUTER socket with comprehensive
    error handling and monitoring.
    """

    def __init__(
        self,
        router_address: str = DRouter.DEFAULT_ROUTER_ADDRESS,
        router_port: int = DRouter.DEFAULT_ROUTER_PORT,
        log_level: str = "INFO",
        client_timeout: float = DRouter.DEFAULT_CLIENT_TIMEOUT,
        max_clients: int = 100,
    ):
        """
        Initialize the Hydra Router.

        Args:
            router_address: Address to bind the router socket
            router_port: Port to bind the router socket
            log_level: Logging level
            client_timeout: Timeout for client heartbeats in seconds
            max_clients: Maximum number of concurrent clients
        """
        self.router_address = router_address
        self.router_port = router_port
        self.client_timeout = client_timeout
        self.max_clients = max_clients

        # ZeroMQ components
        self.context: Optional[zmq.asyncio.Context] = None
        self.socket: Optional[zmq.asyncio.Socket] = None

        # Core components
        self.client_registry = ClientRegistry()
        self.message_router: Optional[MessageRouter] = None
        self.validator = MessageValidator()

        # Background tasks
        self.request_handler_task: Optional[asyncio.Task] = None
        self.client_pruner_task: Optional[asyncio.Task] = None

        # State management
        self.running = False
        self.shutdown_event = asyncio.Event()

        # Logging
        self.logger = logging.getLogger("hydra_router.router")
        self.logger.setLevel(getattr(logging, log_level.upper()))

    async def start(self) -> None:
        """Start the Hydra Router."""
        if self.running:
            self.logger.warning("Router is already running")
            return

        try:
            self.logger.info(
                f"Starting Hydra Router on {self.router_address}:{self.router_port}"
            )

            # Create ZeroMQ context and socket
            self.context = zmq.asyncio.Context()
            self.socket = self.context.socket(zmq.ROUTER)

            # Set socket options
            self.socket.setsockopt(zmq.LINGER, 1000)  # 1 second linger
            self.socket.setsockopt(
                zmq.ROUTER_MANDATORY, 1
            )  # Fail on unroutable messages

            # Bind to address
            bind_address = f"tcp://{self.router_address}:{self.router_port}"
            self.socket.bind(bind_address)

            # Initialize message router
            self.message_router = MessageRouter(self.client_registry, self.socket)

            # Start background tasks
            await self.start_background_tasks()

            self.running = True
            self.logger.info(f"Hydra Router started successfully on {bind_address}")

        except Exception as e:
            self.logger.error(f"Failed to start router: {e}")
            await self.cleanup()
            raise ConnectionError(f"Failed to start router: {e}")

    async def start_background_tasks(self) -> None:
        """Start background tasks for request handling and client management."""
        self.request_handler_task = asyncio.create_task(self.handle_requests())
        self.client_pruner_task = asyncio.create_task(self.prune_dead_clients())

    async def handle_requests(self) -> None:
        """Main request handling loop."""
        while self.running and not self.shutdown_event.is_set():
            try:
                # Check if socket is available
                if not self.socket:
                    self.logger.error("Socket not available")
                    break

                # Receive message with timeout
                frames = await asyncio.wait_for(
                    self.socket.recv_multipart(), timeout=1.0
                )

                if len(frames) != 2:
                    self.logger.error(f"Invalid frame count: {len(frames)}")
                    continue

                identity = frames[0]
                identity_str = identity.decode()
                msg_bytes = frames[1]

                # Parse JSON message
                try:
                    message = zmq.utils.jsonapi.loads(msg_bytes)
                    # Ensure message is a dictionary
                    if not isinstance(message, dict):
                        self.logger.error(
                            f"Message is not a dictionary: {type(message)}"
                        )
                        continue
                except (ValueError, TypeError) as e:
                    self._log_json_parse_error(msg_bytes, e, identity_str)
                    continue

                # Validate message format
                is_valid, error = self.validator.validate_router_message(message)
                if not is_valid:
                    self._log_malformed_message(message, error, identity_str)
                    continue

                # Register client if not already registered
                await self._ensure_client_registered(identity_str, message)

                # Route the message
                if self.message_router:
                    await self.message_router.route_message(identity_str, message)

            except asyncio.TimeoutError:
                # Normal timeout, continue loop
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in request handler: {e}")
                continue

    async def _ensure_client_registered(
        self, client_id: str, message: Dict[str, Any]
    ) -> None:
        """Ensure a client is registered in the registry."""
        registry_data = await self.client_registry.get_registry_data()

        if client_id not in registry_data:
            client_type = message.get(DRouter.SENDER)
            if client_type:
                await self.client_registry.register_client(client_id, client_type)

                # Check client limit
                client_count = await self.client_registry.get_client_count()
                if client_count > self.max_clients:
                    self.logger.warning(
                        f"Client count ({client_count}) exceeds maximum ({self.max_clients})"
                    )

    async def prune_dead_clients(self) -> None:
        """Background task to prune inactive clients."""
        while self.running and not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(
                    self.client_timeout / 2
                )  # Check twice per timeout period

                if self.running:
                    removed_clients = await self.client_registry.prune_inactive_clients(
                        self.client_timeout
                    )
                    if removed_clients:
                        self.logger.info(
                            f"Pruned {len(removed_clients)} inactive clients"
                        )

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in client pruner: {e}")

    async def shutdown(self) -> None:
        """Shutdown the Hydra Router gracefully."""
        if not self.running:
            return

        self.logger.info("Shutting down Hydra Router")
        self.running = False
        self.shutdown_event.set()

        # Cancel background tasks
        if self.request_handler_task:
            self.request_handler_task.cancel()
            try:
                await self.request_handler_task
            except asyncio.CancelledError:
                pass

        if self.client_pruner_task:
            self.client_pruner_task.cancel()
            try:
                await self.client_pruner_task
            except asyncio.CancelledError:
                pass

        await self.cleanup()
        self.logger.info("Hydra Router shutdown complete")

    async def cleanup(self) -> None:
        """Clean up ZeroMQ resources."""
        if self.socket:
            self.socket.close()
            self.socket = None

        if self.context:
            self.context.term()
            self.context = None

    def _log_malformed_message(
        self, message: Dict[str, Any], error: str, client_identity: str
    ) -> None:
        """Log detailed information about malformed messages."""
        self.logger.error(f"Malformed message from client {client_identity}: {error}")

        # Log expected vs actual format
        expected_format = {
            DRouter.SENDER: "string (HydraClient|HydraServer|CustomApp)",
            DRouter.ELEM: "string (message type)",
            DRouter.DATA: "dict (optional)",
            DRouter.CLIENT_ID: "string (optional)",
            DRouter.TIMESTAMP: "float (optional)",
            DRouter.REQUEST_ID: "string (optional)",
        }
        self.logger.error(f"Expected format: {expected_format}")

        # Log actual message (truncated for safety)
        actual_message = str(message)
        if len(actual_message) > 500:
            actual_message = actual_message[:500] + "... (truncated)"
        self.logger.error(f"Actual message: {actual_message}")

        # Provide debugging hints
        if isinstance(message, dict):
            present_fields = list(message.keys())
            self.logger.error(f"Present fields: {present_fields}")
            field_types = {k: type(v).__name__ for k, v in message.items()}
            self.logger.error(f"Field types: {field_types}")

        self.logger.error(
            "Debugging hints: Check MQClient format conversion is working correctly"
        )

    def _log_json_parse_error(
        self, msg_bytes: bytes, error: Exception, client_identity: str
    ) -> None:
        """Log detailed information about JSON parsing errors."""
        self.logger.error(f"JSON parsing error from client {client_identity}: {error}")

        try:
            msg_str = msg_bytes.decode("utf-8", errors="replace")
        except Exception:
            msg_str = str(msg_bytes)

        if len(msg_str) > 300:
            msg_str = msg_str[:300] + "... (truncated)"

        self.logger.error(f"Actual message bytes: {msg_str}")
        self.logger.error(f"Message length: {len(msg_bytes)} bytes")

    async def get_status(self) -> Dict[str, Any]:
        """
        Get router status information.

        Returns:
            Dictionary with router status
        """
        registry_data = await self.client_registry.get_registry_data()

        return {
            "running": self.running,
            "address": f"tcp://{self.router_address}:{self.router_port}",
            "client_count": len(registry_data),
            "has_server": await self.client_registry.has_server(),
            "server_id": self.client_registry.server_id,
            "clients": registry_data,
            "max_clients": self.max_clients,
            "client_timeout": self.client_timeout,
        }


async def run_router(
    address: str = DRouter.DEFAULT_ROUTER_ADDRESS,
    port: int = RouterConstants.DEFAULT_ROUTER_PORT,
    log_level: str = "INFO",
) -> None:
    """
    Run the Hydra Router with signal handling.

    Args:
        address: Router bind address
        port: Router bind port
        log_level: Logging level
    """
    # Set up logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    router = HydraRouter(router_address=address, router_port=port, log_level=log_level)

    # Set up signal handlers for graceful shutdown
    def signal_handler() -> None:
        logging.getLogger("hydra_router").info("Received shutdown signal")
        asyncio.create_task(router.shutdown())

    # Register signal handlers
    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, lambda s, f: signal_handler())

    try:
        await router.start()

        # Wait for shutdown
        await router.shutdown_event.wait()

    except KeyboardInterrupt:
        logging.getLogger("hydra_router").info("Received keyboard interrupt")
    except Exception as e:
        logging.getLogger("hydra_router").error(f"Router error: {e}")
    finally:
        await router.shutdown()


def main() -> None:
    """Main entry point for the hydra-router command."""
    import argparse

    parser = argparse.ArgumentParser(description="Hydra Router - ZeroMQ Message Router")
    parser.add_argument(
        "--address",
        default=RouterConstants.DEFAULT_ROUTER_ADDRESS,
        help=f"Router bind address (default: {RouterConstants.DEFAULT_ROUTER_ADDRESS})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=RouterConstants.DEFAULT_ROUTER_PORT,
        help=f"Router bind port (default: {RouterConstants.DEFAULT_ROUTER_PORT})",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    try:
        asyncio.run(
            run_router(address=args.address, port=args.port, log_level=args.log_level)
        )
    except KeyboardInterrupt:
        print("\nShutdown complete")


if __name__ == "__main__":
    main()
