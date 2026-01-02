"""
Real integration tests for HydraRouter communication.

These tests start actual router processes and test real ZeroMQ communication
without mocks. This ensures the system actually works end-to-end.
"""

import asyncio
import time
from typing import AsyncGenerator, Callable

import pytest

from hydra_router.constants.DMsgType import DMsgType
from hydra_router.constants.DRouter import DRouter
from hydra_router.mq_client import MQClient, ZMQMessage
from hydra_router.router import HydraRouter


class TestRealCommunication:
    """Test real communication between router, clients, and servers."""

    @pytest.fixture  # type: ignore[misc]
    async def router(self) -> AsyncGenerator[HydraRouter, None]:
        """Start a real router for testing."""
        router = HydraRouter(
            router_address="127.0.0.1",
            router_port=5557,  # Use different port to avoid conflicts
            client_timeout=5.0,
        )
        await router.start()
        yield router
        await router.shutdown()

    @pytest.fixture  # type: ignore[misc]
    async def client(self, router: HydraRouter) -> AsyncGenerator[MQClient, None]:
        """Create a real client connected to the test router."""
        client = MQClient(
            router_address="tcp://127.0.0.1:5557",
            client_type=DRouter.SIMPLE_CLIENT,
            client_id="test-client",
        )
        await client.connect()
        # Give time for connection to establish
        await asyncio.sleep(0.1)
        yield client
        await client.disconnect()

    @pytest.fixture  # type: ignore[misc]
    async def server(self, router: HydraRouter) -> AsyncGenerator[MQClient, None]:
        """Create a real server connected to the test router."""
        server = MQClient(
            router_address="tcp://127.0.0.1:5557",
            client_type=DRouter.SIMPLE_SERVER,
            client_id="test-server",
        )
        await server.connect()
        # Give time for connection to establish
        await asyncio.sleep(0.1)
        yield server
        await server.disconnect()

    async def test_router_starts_and_stops(self) -> None:
        """Test that router can start and stop properly."""
        router = HydraRouter(
            router_address="127.0.0.1",
            router_port=5558,
        )

        # Router should not be running initially
        assert not router.running

        # Start router
        await router.start()
        assert router.running

        # Get status
        status = await router.get_status()
        assert status["running"] is True
        assert status["client_count"] == 0

        # Stop router
        await router.shutdown()
        assert not router.running

    async def test_client_connects_to_router(self, router: HydraRouter) -> None:
        """Test that client can connect to router."""
        client = MQClient(
            router_address="tcp://127.0.0.1:5557",
            client_type=DRouter.SIMPLE_CLIENT,
            client_id="test-client-connect",
        )

        # Client should not be connected initially
        assert not client.connected

        # Connect client
        await client.connect()
        assert client.connected

        # Give router time to register client
        await asyncio.sleep(0.5)

        # Check router status shows client
        status = await router.get_status()
        assert status["client_count"] == 1
        assert "test-client-connect" in status["clients"]

        # Disconnect client
        await client.disconnect()
        assert not client.connected

    async def test_heartbeat_communication(
        self, router: HydraRouter, client: MQClient
    ) -> None:
        """Test that heartbeat messages work."""
        # Give time for heartbeat to be sent
        await asyncio.sleep(0.5)

        # Check that client is registered
        status = await router.get_status()
        assert status["client_count"] == 1
        assert "test-client" in status["clients"]

    async def test_client_server_square_calculation(
        self, router: HydraRouter, client: MQClient, server: MQClient
    ) -> None:
        """Test real client-server communication for square calculation."""
        # Set up response tracking
        received_responses = []

        def handle_square_response(message: ZMQMessage) -> None:
            received_responses.append(message)

        def handle_square_request(message: ZMQMessage) -> None:
            data = message.data or {}
            number = data.get("number", 0)
            result = number * number

            # Send response
            response = ZMQMessage(
                message_type=DMsgType.SQUARE_RESPONSE,
                timestamp=time.time(),
                client_id="test-server",
                request_id=message.request_id,
                data={"number": number, "result": result},
            )

            asyncio.create_task(server.send_message(response))

        # Register handlers
        client.register_message_handler(
            DMsgType.SQUARE_RESPONSE, handle_square_response
        )
        server.register_message_handler(DMsgType.SQUARE_REQUEST, handle_square_request)

        # Give time for handlers to be registered and connections to stabilize
        await asyncio.sleep(0.5)

        # Send square request
        request = ZMQMessage(
            message_type=DMsgType.SQUARE_REQUEST,
            timestamp=time.time(),
            client_id="test-client",
            request_id="test-req-1",
            data={"number": 5},
        )

        await client.send_message(request)

        # Wait for response
        await asyncio.sleep(1.0)

        # Check that response was received
        assert len(received_responses) == 1
        response = received_responses[0]
        assert response.message_type == DMsgType.SQUARE_RESPONSE
        assert response.request_id == "test-req-1"
        assert response.data is not None
        assert response.data["number"] == 5
        assert response.data["result"] == 25

    async def test_multiple_clients_communication(self, router: HydraRouter) -> None:
        """Test communication with multiple clients."""
        # Create multiple clients
        clients = []
        for i in range(3):
            client = MQClient(
                router_address="tcp://127.0.0.1:5557",
                client_type=DRouter.SIMPLE_CLIENT,
                client_id=f"test-client-{i}",
            )
            await client.connect()
            clients.append(client)

        # Give router time to register all clients
        await asyncio.sleep(1.0)

        # Check router status
        status = await router.get_status()
        assert status["client_count"] == 3

        for i in range(3):
            assert f"test-client-{i}" in status["clients"]

        # Clean up
        for client in clients:
            await client.disconnect()

    async def test_server_broadcast_to_clients(self, router: HydraRouter) -> None:
        """Test server broadcasting messages to multiple clients."""
        # Create server
        server = MQClient(
            router_address="tcp://127.0.0.1:5557",
            client_type=DRouter.SIMPLE_SERVER,
            client_id="broadcast-server",
        )
        await server.connect()

        # Create multiple clients
        clients = []
        received_messages = []

        def create_handler(client_id: str) -> Callable[[ZMQMessage], None]:
            def handle_broadcast(message: ZMQMessage) -> None:
                received_messages.append((client_id, message))

            return handle_broadcast

        for i in range(2):
            client = MQClient(
                router_address="tcp://127.0.0.1:5557",
                client_type=DRouter.SIMPLE_CLIENT,
                client_id=f"broadcast-client-{i}",
            )
            await client.connect()
            client.register_message_handler(
                DMsgType.SQUARE_RESPONSE, create_handler(f"broadcast-client-{i}")
            )
            clients.append(client)

        # Give time for connections to stabilize
        await asyncio.sleep(0.5)

        # Server sends broadcast message
        broadcast = ZMQMessage(
            message_type=DMsgType.SQUARE_RESPONSE,
            timestamp=time.time(),
            client_id="broadcast-server",
            data={"broadcast": "Hello all clients!"},
        )

        await server.send_message(broadcast)

        # Wait for messages to be received
        await asyncio.sleep(1.0)

        # Check that all clients received the broadcast
        assert len(received_messages) == 2

        client_ids = [msg[0] for msg in received_messages]
        assert "broadcast-client-0" in client_ids
        assert "broadcast-client-1" in client_ids

        # Clean up
        for client in clients:
            await client.disconnect()
        await server.disconnect()

    async def test_client_registry_request(
        self, router: HydraRouter, client: MQClient
    ) -> None:
        """Test client registry request functionality."""
        received_responses = []

        def handle_registry_response(message: ZMQMessage) -> None:
            received_responses.append(message)

        client.register_message_handler(
            DMsgType.CLIENT_REGISTRY_RESPONSE, handle_registry_response
        )

        # Give time for handler registration
        await asyncio.sleep(0.2)

        # Send registry request
        request = ZMQMessage(
            message_type=DMsgType.CLIENT_REGISTRY_REQUEST,
            timestamp=time.time(),
            client_id="test-client",
            request_id="registry-req-1",
        )

        await client.send_message(request)

        # Wait for response
        await asyncio.sleep(1.0)

        # Check response
        assert len(received_responses) == 1
        response = received_responses[0]
        assert response.message_type == DMsgType.CLIENT_REGISTRY_RESPONSE
        assert response.request_id == "registry-req-1"
        assert response.data is not None
        # The response data contains client information directly
        assert "test-client" in response.data

    async def test_error_handling_no_server(
        self, router: HydraRouter, client: MQClient
    ) -> None:
        """Test error handling when no server is available."""
        received_errors = []

        def handle_error(message: ZMQMessage) -> None:
            received_errors.append(message)

        client.register_message_handler(DMsgType.ERROR, handle_error)

        # Give time for handler registration
        await asyncio.sleep(0.2)

        # Send request without server
        request = ZMQMessage(
            message_type=DMsgType.SQUARE_REQUEST,
            timestamp=time.time(),
            client_id="test-client",
            request_id="no-server-req",
            data={"number": 5},
        )

        await client.send_message(request)

        # Wait for error response
        await asyncio.sleep(1.0)

        # Check error response
        assert len(received_errors) == 1
        error = received_errors[0]
        assert error.message_type == DMsgType.ERROR
        assert error.request_id == "no-server-req"
        assert error.data is not None
        assert "No server connected" in error.data.get("message", "")
