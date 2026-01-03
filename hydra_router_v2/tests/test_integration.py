"""
Integration tests for Hydra Router v2.

These tests validate end-to-end message delivery through the MQClient network
abstraction layer as required by the specifications. Tests cover the complete
communication flow: client > router > server > router > client.
"""

import asyncio
import time
from typing import Any, Dict, List

import pytest

from ..constants.DLog import DLog
from ..constants.DMsgType import DMsgType
from ..constants.DRouter import DRouter
from ..hydra_router import HydraRouter
from ..mq_client import MQClient
from ..zmq_message import ZMQMessage


class TestIntegration:
    """Integration tests for complete message flow validation."""

    @pytest.fixture
    async def router(self) -> HydraRouter:
        """Create and start a test router."""
        router = HydraRouter(
            router_address="localhost",
            router_port=5557,  # Use different port for tests
            log_level=DLog.DEBUG,  # Enable DEBUG logging for tests
            heartbeat_timeout=10.0,
        )
        await router.start()

        # Give router time to start
        await asyncio.sleep(0.1)

        yield router

        await router.stop()

    @pytest.fixture
    async def client(self, router: HydraRouter) -> MQClient:
        """Create and connect a test client."""
        client = MQClient(
            router_address="tcp://localhost:5557",
            client_type=DRouter.SIMPLE_CLIENT,
            client_id="test-client",
            log_level=DLog.DEBUG,
        )
        await client.connect()

        # Give client time to connect
        await asyncio.sleep(0.1)

        yield client

        await client.disconnect()

    @pytest.fixture
    async def server(self, router: HydraRouter) -> MQClient:
        """Create and connect a test server."""
        server = MQClient(
            router_address="tcp://localhost:5557",
            client_type=DRouter.SIMPLE_SERVER,
            client_id="test-server",
            log_level=DLog.DEBUG,
        )
        await server.connect()

        # Give server time to connect
        await asyncio.sleep(0.1)

        yield server

        await server.disconnect()

    async def test_client_connects_to_router(self, router: HydraRouter) -> None:
        """Test that client can connect to router successfully."""
        client = MQClient(
            router_address="tcp://localhost:5557",
            client_type=DRouter.SIMPLE_CLIENT,
            client_id="connection-test-client",
            log_level=DLog.DEBUG,
        )

        # Test connection
        await client.connect()
        assert client.is_connected

        # Verify client is registered
        await asyncio.sleep(0.2)  # Allow heartbeat to register
        status = await router.get_status()
        assert status["client_count"] >= 1

        await client.disconnect()
        assert not client.is_connected

    async def test_server_connects_to_router(self, router: HydraRouter) -> None:
        """Test that server can connect to router successfully."""
        server = MQClient(
            router_address="tcp://localhost:5557",
            client_type=DRouter.SIMPLE_SERVER,
            client_id="connection-test-server",
            log_level=DLog.DEBUG,
        )

        # Test connection
        await server.connect()
        assert server.is_connected

        # Verify server is registered
        await asyncio.sleep(0.2)  # Allow heartbeat to register
        status = await router.get_status()
        assert status["has_server"]
        assert status["server_id"] == "connection-test-server"

        await server.disconnect()
        assert not server.is_connected

    async def test_client_to_server_message_flow(
        self, router: HydraRouter, client: MQClient, server: MQClient
    ) -> None:
        """
        Test complete message flow: client > router > server.

        Validates that messages sent by client are properly routed to server
        through the MQClient network abstraction layer.
        """
        received_messages: List[ZMQMessage] = []

        def handle_request(message: ZMQMessage) -> None:
            """Handler to capture received messages."""
            received_messages.append(message)

        # Register handler on server
        server.register_message_handler(DMsgType.SQUARE_REQUEST, handle_request)

        # Send message from client
        test_message = ZMQMessage(
            message_type=DMsgType.SQUARE_REQUEST,
            client_id="test-client",
            request_id="test-req-123",
            data={"number": 42},
        )

        await client.send_message(test_message)

        # Wait for message to be processed
        await asyncio.sleep(0.5)

        # Verify message was received by server
        assert len(received_messages) == 1
        received = received_messages[0]

        assert received.message_type == DMsgType.SQUARE_REQUEST
        assert received.client_id == "test-client"
        assert received.request_id == "test-req-123"
        assert received.data == {"number": 42}

    async def test_server_to_client_message_flow(
        self, router: HydraRouter, client: MQClient, server: MQClient
    ) -> None:
        """
        Test complete response flow: server > router > client.

        Validates that responses sent by server are properly broadcast to
        all clients through the MQClient network abstraction layer.
        """
        received_responses: List[ZMQMessage] = []

        def handle_response(message: ZMQMessage) -> None:
            """Handler to capture received responses."""
            received_responses.append(message)

        # Register handler on client
        client.register_message_handler(DMsgType.SQUARE_RESPONSE, handle_response)

        # Send response from server
        response_message = ZMQMessage(
            message_type=DMsgType.SQUARE_RESPONSE,
            client_id="test-server",
            request_id="test-req-456",
            data={"number": 25, "result": 625},
        )

        await server.send_message(response_message)

        # Wait for message to be processed
        await asyncio.sleep(0.5)

        # Verify response was received by client
        assert len(received_responses) == 1
        received = received_responses[0]

        assert received.message_type == DMsgType.SQUARE_RESPONSE
        assert received.client_id == "test-server"
        assert received.request_id == "test-req-456"
        assert received.data == {"number": 25, "result": 625}

    async def test_complete_request_response_cycle(
        self, router: HydraRouter, client: MQClient, server: MQClient
    ) -> None:
        """
        Test complete request-response cycle with proper message correlation.

        Validates the complete communication flow:
        1. Client sends request to server through router
        2. Server receives request and sends response back through router
        3. Client receives response with proper request correlation

        This test ensures the MQClient properly abstracts the network layer
        for both client and server applications.
        """
        received_requests: List[ZMQMessage] = []
        received_responses: List[ZMQMessage] = []

        async def handle_square_request(message: ZMQMessage) -> None:
            """Server handler that processes requests and sends responses."""
            received_requests.append(message)

            # Extract request data
            data = message.data or {}
            number = data.get("number", 0)
            result = number * number

            # Send response with same request_id for correlation
            response = ZMQMessage(
                message_type=DMsgType.SQUARE_RESPONSE,
                client_id="test-server",
                request_id=message.request_id,  # CRITICAL: preserve request_id
                data={"number": number, "result": result, "server_id": "test-server"},
            )

            await server.send_message(response)

        def handle_square_response(message: ZMQMessage) -> None:
            """Client handler that captures responses."""
            received_responses.append(message)

        # Register handlers
        server.register_message_handler(DMsgType.SQUARE_REQUEST, handle_square_request)
        client.register_message_handler(
            DMsgType.SQUARE_RESPONSE, handle_square_response
        )

        # Send request from client
        request = ZMQMessage(
            message_type=DMsgType.SQUARE_REQUEST,
            client_id="test-client",
            request_id="complete-cycle-test",
            data={"number": 7},
        )

        await client.send_message(request)

        # Wait for complete cycle to finish
        await asyncio.sleep(1.0)

        # Verify request was received by server
        assert len(received_requests) == 1
        req = received_requests[0]
        assert req.message_type == DMsgType.SQUARE_REQUEST
        assert req.request_id == "complete-cycle-test"
        assert req.data == {"number": 7}

        # Verify response was received by client
        assert len(received_responses) == 1
        resp = received_responses[0]
        assert resp.message_type == DMsgType.SQUARE_RESPONSE
        assert resp.request_id == "complete-cycle-test"  # Proper correlation
        assert resp.data == {"number": 7, "result": 49, "server_id": "test-server"}

    async def test_multiple_clients_receive_server_broadcast(
        self, router: HydraRouter, server: MQClient
    ) -> None:
        """
        Test that server messages are broadcast to all connected clients.

        Validates the router's broadcasting capability and ensures all clients
        receive server responses through the MQClient network abstraction.
        """
        # Create multiple clients
        clients = []
        received_messages = [[] for _ in range(3)]

        for i in range(3):
            client = MQClient(
                router_address="tcp://localhost:5557",
                client_type=DRouter.SIMPLE_CLIENT,
                client_id=f"broadcast-client-{i}",
                log_level=DLog.DEBUG,
            )
            await client.connect()

            # Create handler that captures messages for this client
            def create_handler(client_index: int):
                def handler(message: ZMQMessage) -> None:
                    received_messages[client_index].append(message)

                return handler

            client.register_message_handler(DMsgType.SQUARE_RESPONSE, create_handler(i))
            clients.append(client)

        # Wait for clients to connect
        await asyncio.sleep(0.5)

        # Send broadcast message from server
        broadcast_message = ZMQMessage(
            message_type=DMsgType.SQUARE_RESPONSE,
            client_id="test-server",
            data={"broadcast": True, "message": "Hello all clients!"},
        )

        await server.send_message(broadcast_message)

        # Wait for broadcast to complete
        await asyncio.sleep(0.5)

        # Verify all clients received the message
        for i, messages in enumerate(received_messages):
            assert len(messages) == 1, f"Client {i} should receive 1 message"
            msg = messages[0]
            assert msg.message_type == DMsgType.SQUARE_RESPONSE
            assert msg.data == {"broadcast": True, "message": "Hello all clients!"}

        # Cleanup
        for client in clients:
            await client.disconnect()

    async def test_no_server_connected_error(self, router: HydraRouter) -> None:
        """
        Test that clients receive 'no server connected' error when no server is available.

        Validates error handling when client sends request but no server is connected.
        """
        client = MQClient(
            router_address="tcp://localhost:5557",
            client_type=DRouter.SIMPLE_CLIENT,
            client_id="no-server-test-client",
            log_level=DLog.DEBUG,
        )
        await client.connect()

        received_errors: List[ZMQMessage] = []

        def handle_error(message: ZMQMessage) -> None:
            """Handler to capture error messages."""
            received_errors.append(message)

        # Register error handler
        client.register_message_handler(DMsgType.NO_SERVER_CONNECTED, handle_error)

        # Send request when no server is connected
        request = ZMQMessage(
            message_type=DMsgType.SQUARE_REQUEST,
            client_id="no-server-test-client",
            request_id="no-server-test",
            data={"number": 10},
        )

        await client.send_message(request)

        # Wait for error response
        await asyncio.sleep(0.5)

        # Verify error was received
        assert len(received_errors) == 1
        error = received_errors[0]
        assert error.message_type == DMsgType.NO_SERVER_CONNECTED
        assert error.request_id == "no-server-test"
        assert "No server connected" in str(error.data)

        await client.disconnect()

    async def test_message_format_conversion(
        self, router: HydraRouter, client: MQClient, server: MQClient
    ) -> None:
        """
        Test that MQClient properly converts between ZMQMessage and DRouter formats.

        Validates the Message_Format_Adapter functionality by ensuring message
        content is preserved during format conversion.
        """
        received_messages: List[ZMQMessage] = []

        def capture_message(message: ZMQMessage) -> None:
            """Capture received message for validation."""
            received_messages.append(message)

        server.register_message_handler(DMsgType.SQUARE_REQUEST, capture_message)

        # Send message with all optional fields
        original = ZMQMessage(
            message_type=DMsgType.SQUARE_REQUEST,
            timestamp=1234567890.123,
            client_id="format-test-client",
            request_id="format-test-req",
            data={
                "number": 15,
                "metadata": {"test": True, "nested": {"value": 42}},
                "array": [1, 2, 3],
            },
        )

        await client.send_message(original)
        await asyncio.sleep(0.5)

        # Verify message was received with all content preserved
        assert len(received_messages) == 1
        received = received_messages[0]

        # Verify all fields are preserved
        assert received.message_type == original.message_type
        assert received.client_id == original.client_id
        assert received.request_id == original.request_id
        assert received.data == original.data
        # Note: timestamp may be slightly different due to conversion timing

    async def test_heartbeat_monitoring(self, router: HydraRouter) -> None:
        """
        Test that heartbeat monitoring properly tracks client connectivity.

        Validates the Heartbeat_Monitor functionality and client registry updates.
        """
        client = MQClient(
            router_address="tcp://localhost:5557",
            client_type=DRouter.SIMPLE_CLIENT,
            client_id="heartbeat-test-client",
            heartbeat_interval=1.0,  # Fast heartbeat for testing
            log_level=DLog.DEBUG,
        )

        await client.connect()

        # Wait for initial heartbeat and registration
        await asyncio.sleep(1.5)

        # Verify client is registered
        status = await router.get_status()
        assert status["client_count"] >= 1

        # Get registry data to verify heartbeat timestamp
        registry_data = await router.client_registry.get_registry_data()
        assert "heartbeat-test-client" in registry_data

        client_info = registry_data["heartbeat-test-client"]
        initial_heartbeat = client_info["last_heartbeat"]

        # Wait for another heartbeat
        await asyncio.sleep(2.0)

        # Verify heartbeat was updated
        registry_data = await router.client_registry.get_registry_data()
        updated_heartbeat = registry_data["heartbeat-test-client"]["last_heartbeat"]

        assert updated_heartbeat > initial_heartbeat

        await client.disconnect()


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
