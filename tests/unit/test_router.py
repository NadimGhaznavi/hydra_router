"""
Unit tests for HydraRouter module.

Tests the HydraRouter, ClientRegistry, and MessageRouter classes
and their core functionality.
"""

import asyncio
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest

from hydra_router.exceptions import ConnectionError
from hydra_router.router import ClientRegistry, HydraRouter, MessageRouter
from hydra_router.router_constants import RouterConstants


class TestClientRegistry:
    """Test ClientRegistry class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = ClientRegistry()

    async def test_register_client(self):
        """Test registering a client."""
        client_id = "client-123"
        client_type = RouterConstants.HYDRA_CLIENT

        await self.registry.register_client(client_id, client_type)

        registry_data = await self.registry.get_registry_data()
        assert client_id in registry_data
        assert registry_data[client_id]["client_type"] == client_type
        assert not registry_data[client_id]["is_server"]

    async def test_register_server(self):
        """Test registering a server."""
        server_id = "server-123"
        server_type = RouterConstants.HYDRA_SERVER

        await self.registry.register_client(server_id, server_type)

        registry_data = await self.registry.get_registry_data()
        assert server_id in registry_data
        assert registry_data[server_id]["client_type"] == server_type
        assert registry_data[server_id]["is_server"]
        assert self.registry.server_id == server_id

    async def test_register_multiple_servers_replaces_previous(self):
        """Test that registering multiple servers replaces the previous one."""
        server1_id = "server-1"
        server2_id = "server-2"
        server_type = RouterConstants.HYDRA_SERVER

        await self.registry.register_client(server1_id, server_type)
        assert self.registry.server_id == server1_id

        await self.registry.register_client(server2_id, server_type)
        assert self.registry.server_id == server2_id

    async def test_update_heartbeat(self):
        """Test updating client heartbeat."""
        client_id = "client-123"
        client_type = RouterConstants.HYDRA_CLIENT

        await self.registry.register_client(client_id, client_type)

        # Get initial heartbeat
        registry_data = await self.registry.get_registry_data()
        initial_heartbeat = registry_data[client_id]["last_heartbeat"]

        # Wait a bit and update heartbeat
        await asyncio.sleep(0.01)
        await self.registry.update_heartbeat(client_id)

        # Check heartbeat was updated
        registry_data = await self.registry.get_registry_data()
        updated_heartbeat = registry_data[client_id]["last_heartbeat"]
        assert updated_heartbeat > initial_heartbeat

    async def test_update_heartbeat_nonexistent_client(self):
        """Test updating heartbeat for non-existent client."""
        # Should not raise an exception
        await self.registry.update_heartbeat("nonexistent-client")

    async def test_remove_client(self):
        """Test removing a client."""
        client_id = "client-123"
        client_type = RouterConstants.HYDRA_CLIENT

        await self.registry.register_client(client_id, client_type)
        await self.registry.remove_client(client_id)

        registry_data = await self.registry.get_registry_data()
        assert client_id not in registry_data

    async def test_remove_server_clears_server_id(self):
        """Test that removing a server clears the server_id."""
        server_id = "server-123"
        server_type = RouterConstants.HYDRA_SERVER

        await self.registry.register_client(server_id, server_type)
        assert self.registry.server_id == server_id

        await self.registry.remove_client(server_id)
        assert self.registry.server_id is None

    async def test_get_clients_by_type(self):
        """Test getting clients by type."""
        client1_id = "client-1"
        client2_id = "client-2"
        server_id = "server-1"

        await self.registry.register_client(client1_id, RouterConstants.HYDRA_CLIENT)
        await self.registry.register_client(client2_id, RouterConstants.SIMPLE_CLIENT)
        await self.registry.register_client(server_id, RouterConstants.HYDRA_SERVER)

        hydra_clients = await self.registry.get_clients_by_type(
            RouterConstants.HYDRA_CLIENT
        )
        simple_clients = await self.registry.get_clients_by_type(
            RouterConstants.SIMPLE_CLIENT
        )
        servers = await self.registry.get_clients_by_type(RouterConstants.HYDRA_SERVER)

        assert client1_id in hydra_clients
        assert client2_id in simple_clients
        assert server_id in servers
        assert len(hydra_clients) == 1
        assert len(simple_clients) == 1
        assert len(servers) == 1

    async def test_prune_inactive_clients(self):
        """Test pruning inactive clients."""
        client_id = "client-123"
        client_type = RouterConstants.HYDRA_CLIENT

        await self.registry.register_client(client_id, client_type)

        # Wait a bit to ensure client becomes inactive
        await asyncio.sleep(0.01)

        # Prune with very short timeout
        removed_clients = await self.registry.prune_inactive_clients(0.001)

        assert client_id in removed_clients
        registry_data = await self.registry.get_registry_data()
        assert client_id not in registry_data

    async def test_prune_inactive_server_clears_server_id(self):
        """Test that pruning inactive server clears server_id."""
        server_id = "server-123"
        server_type = RouterConstants.HYDRA_SERVER

        await self.registry.register_client(server_id, server_type)
        assert self.registry.server_id == server_id

        # Wait a bit to ensure server becomes inactive
        await asyncio.sleep(0.01)

        # Prune with very short timeout
        removed_clients = await self.registry.prune_inactive_clients(0.001)

        assert server_id in removed_clients
        assert self.registry.server_id is None

    async def test_has_server(self):
        """Test checking if server is connected."""
        assert not await self.registry.has_server()

        server_id = "server-123"
        await self.registry.register_client(server_id, RouterConstants.HYDRA_SERVER)

        assert await self.registry.has_server()

        await self.registry.remove_client(server_id)

        assert not await self.registry.has_server()

    async def test_get_client_count(self):
        """Test getting client count."""
        assert await self.registry.get_client_count() == 0

        await self.registry.register_client("client-1", RouterConstants.HYDRA_CLIENT)
        assert await self.registry.get_client_count() == 1

        await self.registry.register_client("client-2", RouterConstants.SIMPLE_CLIENT)
        assert await self.registry.get_client_count() == 2

        await self.registry.remove_client("client-1")
        assert await self.registry.get_client_count() == 1


class TestMessageRouter:
    """Test MessageRouter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = ClientRegistry()
        self.mock_socket = AsyncMock()
        self.router = MessageRouter(self.registry, self.mock_socket)

    async def test_route_client_heartbeat(self):
        """Test routing client heartbeat message."""
        client_id = "client-123"
        await self.registry.register_client(client_id, RouterConstants.HYDRA_CLIENT)

        message = {
            RouterConstants.SENDER: RouterConstants.HYDRA_CLIENT,
            RouterConstants.ELEM: RouterConstants.HEARTBEAT,
            RouterConstants.CLIENT_ID: client_id,
            RouterConstants.TIMESTAMP: time.time(),
        }

        await self.router.route_message(client_id, message)

        # Heartbeat should not be forwarded, just update registry
        self.mock_socket.send_multipart.assert_not_called()

    async def test_route_client_message_to_server(self):
        """Test routing client message to server."""
        client_id = "client-123"
        server_id = "server-456"

        await self.registry.register_client(client_id, RouterConstants.HYDRA_CLIENT)
        await self.registry.register_client(server_id, RouterConstants.HYDRA_SERVER)

        message = {
            RouterConstants.SENDER: RouterConstants.HYDRA_CLIENT,
            RouterConstants.ELEM: RouterConstants.SQUARE_REQUEST,
            RouterConstants.DATA: {"number": 5},
            RouterConstants.CLIENT_ID: client_id,
            RouterConstants.TIMESTAMP: time.time(),
        }

        await self.router.route_message(client_id, message)

        # Message should be forwarded to server
        self.mock_socket.send_multipart.assert_called_once()
        call_args = self.mock_socket.send_multipart.call_args[0][0]
        assert call_args[0] == server_id.encode()

    async def test_route_client_message_no_server(self):
        """Test routing client message when no server is connected."""
        client_id = "client-123"

        await self.registry.register_client(client_id, RouterConstants.HYDRA_CLIENT)

        message = {
            RouterConstants.SENDER: RouterConstants.HYDRA_CLIENT,
            RouterConstants.ELEM: RouterConstants.SQUARE_REQUEST,
            RouterConstants.DATA: {"number": 5},
            RouterConstants.CLIENT_ID: client_id,
            RouterConstants.TIMESTAMP: time.time(),
        }

        await self.router.route_message(client_id, message)

        # Should send error response to client
        self.mock_socket.send_multipart.assert_called_once()
        call_args = self.mock_socket.send_multipart.call_args[0][0]
        assert call_args[0] == client_id.encode()

    async def test_route_server_message_broadcast(self):
        """Test routing server message broadcasts to clients."""
        client1_id = "client-1"
        client2_id = "client-2"
        server_id = "server-123"

        await self.registry.register_client(client1_id, RouterConstants.HYDRA_CLIENT)
        await self.registry.register_client(client2_id, RouterConstants.SIMPLE_CLIENT)
        await self.registry.register_client(server_id, RouterConstants.HYDRA_SERVER)

        message = {
            RouterConstants.SENDER: RouterConstants.HYDRA_SERVER,
            RouterConstants.ELEM: RouterConstants.SQUARE_RESPONSE,
            RouterConstants.DATA: {"result": 25},
            RouterConstants.CLIENT_ID: server_id,
            RouterConstants.TIMESTAMP: time.time(),
        }

        await self.router.route_message(server_id, message)

        # Should broadcast to both clients
        assert self.mock_socket.send_multipart.call_count == 2

    async def test_route_client_registry_request(self):
        """Test routing client registry request."""
        client_id = "client-123"
        await self.registry.register_client(client_id, RouterConstants.HYDRA_CLIENT)

        message = {
            RouterConstants.SENDER: RouterConstants.HYDRA_CLIENT,
            RouterConstants.ELEM: RouterConstants.CLIENT_REGISTRY_REQUEST,
            RouterConstants.CLIENT_ID: client_id,
            RouterConstants.REQUEST_ID: "req-456",
            RouterConstants.TIMESTAMP: time.time(),
        }

        await self.router.route_message(client_id, message)

        # Should send registry response
        self.mock_socket.send_multipart.assert_called_once()
        call_args = self.mock_socket.send_multipart.call_args[0][0]
        assert call_args[0] == client_id.encode()

    async def test_route_unknown_sender_type(self):
        """Test routing message with unknown sender type."""
        client_id = "client-123"

        message = {
            RouterConstants.SENDER: "UnknownSender",
            RouterConstants.ELEM: RouterConstants.SQUARE_REQUEST,
            RouterConstants.CLIENT_ID: client_id,
            RouterConstants.TIMESTAMP: time.time(),
        }

        # Should not raise exception, just log warning
        await self.router.route_message(client_id, message)

        # No messages should be sent
        self.mock_socket.send_multipart.assert_not_called()


class TestHydraRouter:
    """Test HydraRouter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.router_address = "127.0.0.1"
        self.router_port = 5556

    @patch("hydra_router.router.zmq.asyncio.Context")
    def test_hydra_router_initialization(self, mock_context):
        """Test HydraRouter initialization."""
        router = HydraRouter(
            router_address=self.router_address,
            router_port=self.router_port,
            log_level="DEBUG",
            client_timeout=30.0,
            max_clients=50,
        )

        assert router.router_address == self.router_address
        assert router.router_port == self.router_port
        assert router.client_timeout == 30.0
        assert router.max_clients == 50
        assert not router.running
        assert router.context is None
        assert router.socket is None

    @patch("hydra_router.router.zmq.asyncio.Context")
    def test_hydra_router_default_values(self, mock_context):
        """Test HydraRouter with default values."""
        router = HydraRouter()

        assert router.router_address == RouterConstants.DEFAULT_ROUTER_ADDRESS
        assert router.router_port == RouterConstants.DEFAULT_ROUTER_PORT
        assert router.client_timeout == RouterConstants.DEFAULT_CLIENT_TIMEOUT
        assert router.max_clients == 100

    @patch("hydra_router.router.zmq.asyncio.Context")
    async def test_start_router_success(self, mock_context):
        """Test successful router startup."""
        mock_context_instance = Mock()
        mock_socket_instance = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket_instance

        router = HydraRouter(
            router_address=self.router_address, router_port=self.router_port
        )

        await router.start()

        assert router.running
        assert router.context == mock_context_instance
        assert router.socket == mock_socket_instance

        expected_bind_address = f"tcp://{self.router_address}:{self.router_port}"
        mock_socket_instance.bind.assert_called_once_with(expected_bind_address)

        # Clean up
        await router.shutdown()

    @patch("hydra_router.router.zmq.asyncio.Context")
    async def test_start_router_failure(self, mock_context):
        """Test router startup failure."""
        mock_context_instance = Mock()
        mock_socket_instance = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket_instance
        mock_socket_instance.bind.side_effect = Exception("Bind failed")

        router = HydraRouter(
            router_address=self.router_address, router_port=self.router_port
        )

        with pytest.raises(ConnectionError):
            await router.start()

        assert not router.running

    @patch("hydra_router.router.zmq.asyncio.Context")
    async def test_start_router_already_running(self, mock_context):
        """Test starting router when already running."""
        mock_context_instance = Mock()
        mock_socket_instance = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket_instance

        router = HydraRouter(
            router_address=self.router_address, router_port=self.router_port
        )

        await router.start()

        # Try to start again
        await router.start()

        # Should only bind once
        assert mock_socket_instance.bind.call_count == 1

        # Clean up
        await router.shutdown()

    @patch("hydra_router.router.zmq.asyncio.Context")
    async def test_shutdown_router(self, mock_context):
        """Test router shutdown."""
        mock_context_instance = Mock()
        mock_socket_instance = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket_instance

        router = HydraRouter(
            router_address=self.router_address, router_port=self.router_port
        )

        await router.start()
        await router.shutdown()

        assert not router.running
        mock_socket_instance.close.assert_called_once()
        mock_context_instance.term.assert_called_once()

    @patch("hydra_router.router.zmq.asyncio.Context")
    async def test_get_status(self, mock_context):
        """Test getting router status."""
        mock_context_instance = Mock()
        mock_socket_instance = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket_instance

        router = HydraRouter(
            router_address=self.router_address,
            router_port=self.router_port,
            max_clients=50,
            client_timeout=30.0,
        )

        await router.start()

        status = await router.get_status()

        assert status["running"] is True
        assert status["address"] == f"tcp://{self.router_address}:{self.router_port}"
        assert status["client_count"] == 0
        assert status["has_server"] is False
        assert status["server_id"] is None
        assert status["max_clients"] == 50
        assert status["client_timeout"] == 30.0
        assert "clients" in status

        # Clean up
        await router.shutdown()

    @patch("hydra_router.router.zmq.asyncio.Context")
    async def test_ensure_client_registered(self, mock_context):
        """Test ensuring client is registered."""
        mock_context_instance = Mock()
        mock_socket_instance = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket_instance

        router = HydraRouter()
        await router.start()

        client_id = "client-123"
        message = {
            RouterConstants.SENDER: RouterConstants.HYDRA_CLIENT,
            RouterConstants.ELEM: RouterConstants.HEARTBEAT,
        }

        await router._ensure_client_registered(client_id, message)

        registry_data = await router.client_registry.get_registry_data()
        assert client_id in registry_data
        assert registry_data[client_id]["client_type"] == RouterConstants.HYDRA_CLIENT

        # Clean up
        await router.shutdown()
