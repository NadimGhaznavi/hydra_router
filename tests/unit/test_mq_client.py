"""
Unit tests for MQClient module.

Tests the MQClient class, message format conversion,
and communication functionality.
"""

import asyncio
import time
from dataclasses import dataclass
from enum import Enum
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from hydra_router.exceptions import ConnectionError, MessageFormatError
from hydra_router.mq_client import MessageType, MQClient, ZMQMessage
from hydra_router.router_constants import RouterConstants


class TestZMQMessage:
    """Test ZMQMessage dataclass."""

    def test_zmq_message_creation(self):
        """Test creating ZMQMessage instance."""
        timestamp = time.time()
        message = ZMQMessage(
            message_type=MessageType.SQUARE_REQUEST,
            timestamp=timestamp,
            data={"number": 5},
            client_id="client-123",
            request_id="req-456",
        )

        assert message.message_type == MessageType.SQUARE_REQUEST
        assert message.data == {"number": 5}
        assert message.client_id == "client-123"
        assert message.request_id == "req-456"
        assert message.timestamp == timestamp

    def test_zmq_message_default_timestamp(self):
        """Test that ZMQMessage requires timestamp parameter."""
        # ZMQMessage requires timestamp as a required parameter
        timestamp = time.time()
        message = ZMQMessage(MessageType.HEARTBEAT, timestamp=timestamp)

        assert message.timestamp == timestamp

    def test_zmq_message_custom_timestamp(self):
        """Test ZMQMessage with custom timestamp."""
        custom_timestamp = 1234567890.0
        message = ZMQMessage(MessageType.HEARTBEAT, timestamp=custom_timestamp)

        assert message.timestamp == custom_timestamp

    def test_zmq_message_optional_fields(self):
        """Test ZMQMessage with optional fields."""
        timestamp = time.time()
        message = ZMQMessage(MessageType.HEARTBEAT, timestamp=timestamp)

        assert message.data is None
        assert message.client_id is None
        assert message.request_id is None


class TestMessageType:
    """Test MessageType enum."""

    def test_message_type_enum_values(self):
        """Test that MessageType enum has expected values."""
        assert hasattr(MessageType, "HEARTBEAT")
        assert hasattr(MessageType, "SQUARE_REQUEST")
        assert hasattr(MessageType, "SQUARE_RESPONSE")
        assert hasattr(MessageType, "ERROR")
        assert hasattr(MessageType, "CLIENT_REGISTRY_REQUEST")
        assert hasattr(MessageType, "CLIENT_REGISTRY_RESPONSE")

    def test_message_type_string_values(self):
        """Test that MessageType enum values are strings."""
        for message_type in MessageType:
            assert isinstance(message_type.value, str)
            assert len(message_type.value) > 0


class TestMQClient:
    """Test MQClient class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client_id = "test-client-123"
        self.client_type = RouterConstants.HYDRA_CLIENT
        self.router_address = "tcp://localhost:5556"

    @patch("hydra_router.mq_client.zmq.asyncio.Context")
    def test_mq_client_initialization(self, mock_context):
        """Test MQClient initialization."""
        client = MQClient(
            router_address=self.router_address,
            client_type=self.client_type,
            client_id=self.client_id,
        )

        assert client.client_id == self.client_id
        assert client.client_type == self.client_type
        assert client.router_address == self.router_address
        assert not client.connected
        assert client.context is None
        assert client.socket is None

    @patch("hydra_router.mq_client.zmq.asyncio.Context")
    def test_mq_client_default_values(self, mock_context):
        """Test MQClient with default values."""
        # MQClient requires router_address as first parameter
        client = MQClient(
            router_address="tcp://localhost:5556",
            client_type=self.client_type,
            client_id=self.client_id,
        )

        assert client.router_address == "tcp://localhost:5556"

    @patch("hydra_router.mq_client.zmq.asyncio.Context")
    @patch("hydra_router.mq_client.zmq.asyncio.Socket")
    async def test_connect_success(self, mock_socket, mock_context):
        """Test successful connection."""
        mock_context_instance = Mock()
        mock_socket_instance = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket_instance

        client = MQClient(
            router_address=self.router_address,
            client_type=self.client_type,
            client_id=self.client_id,
        )

        await client.connect()

        assert client.connected
        assert client.context == mock_context_instance
        assert client.socket == mock_socket_instance
        mock_socket_instance.connect.assert_called_once_with(self.router_address)

    @patch("hydra_router.mq_client.zmq.asyncio.Context")
    async def test_connect_failure(self, mock_context):
        """Test connection failure."""
        mock_context_instance = Mock()
        mock_socket_instance = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket_instance
        mock_socket_instance.connect.side_effect = Exception("Connection failed")

        client = MQClient(
            router_address=self.router_address,
            client_type=self.client_type,
            client_id=self.client_id,
        )

        with pytest.raises(ConnectionError):
            await client.connect()

        assert not client.connected

    @patch("hydra_router.mq_client.zmq.asyncio.Context")
    async def test_disconnect(self, mock_context):
        """Test disconnection."""
        mock_context_instance = Mock()
        mock_socket_instance = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket_instance

        client = MQClient(
            router_address=self.router_address,
            client_type=self.client_type,
            client_id=self.client_id,
        )

        await client.connect()
        await client.disconnect()

        assert not client.connected
        mock_socket_instance.close.assert_called_once()
        mock_context_instance.term.assert_called_once()

    def test_convert_to_router_format(self):
        """Test converting ZMQMessage to RouterConstants format."""
        client = MQClient(
            router_address=self.router_address,
            client_type=self.client_type,
            client_id=self.client_id,
        )

        zmq_message = ZMQMessage(
            message_type=MessageType.SQUARE_REQUEST,
            data={"number": 5},
            client_id="client-123",
            request_id="req-456",
            timestamp=1234567890.0,
        )

        router_message = client._convert_to_router_format(zmq_message)

        assert router_message[RouterConstants.SENDER] == self.client_type
        assert router_message[RouterConstants.ELEM] == MessageType.SQUARE_REQUEST.value
        assert router_message[RouterConstants.DATA] == {"number": 5}
        assert router_message[RouterConstants.CLIENT_ID] == "client-123"
        assert router_message[RouterConstants.REQUEST_ID] == "req-456"
        assert router_message[RouterConstants.TIMESTAMP] == 1234567890.0

    def test_convert_to_router_format_minimal(self):
        """Test converting minimal ZMQMessage to RouterConstants format."""
        client = MQClient(
            router_address=self.router_address,
            client_type=self.client_type,
            client_id=self.client_id,
        )

        zmq_message = ZMQMessage(MessageType.HEARTBEAT)
        router_message = client._convert_to_router_format(zmq_message)

        assert router_message[RouterConstants.SENDER] == self.client_type
        assert router_message[RouterConstants.ELEM] == MessageType.HEARTBEAT.value
        assert RouterConstants.TIMESTAMP in router_message

        # Optional fields should not be present if None
        assert RouterConstants.DATA not in router_message
        assert RouterConstants.CLIENT_ID not in router_message
        assert RouterConstants.REQUEST_ID not in router_message

    def test_convert_from_router_format(self):
        """Test converting RouterConstants format to ZMQMessage."""
        client = MQClient(
            router_address=self.router_address,
            client_type=self.client_type,
            client_id=self.client_id,
        )

        router_message = {
            RouterConstants.SENDER: RouterConstants.HYDRA_SERVER,
            RouterConstants.ELEM: MessageType.SQUARE_RESPONSE.value,
            RouterConstants.DATA: {"result": 25},
            RouterConstants.CLIENT_ID: "server-123",
            RouterConstants.REQUEST_ID: "req-456",
            RouterConstants.TIMESTAMP: 1234567890.0,
        }

        zmq_message = client._convert_from_router_format(router_message)

        assert zmq_message.message_type == MessageType.SQUARE_RESPONSE
        assert zmq_message.data == {"result": 25}
        assert zmq_message.client_id == "server-123"
        assert zmq_message.request_id == "req-456"
        assert zmq_message.timestamp == 1234567890.0

    def test_convert_from_router_format_minimal(self):
        """Test converting minimal RouterConstants format to ZMQMessage."""
        client = MQClient(
            router_address=self.router_address,
            client_type=self.client_type,
            client_id=self.client_id,
        )

        router_message = {
            RouterConstants.SENDER: RouterConstants.HYDRA_SERVER,
            RouterConstants.ELEM: MessageType.HEARTBEAT.value,
            RouterConstants.TIMESTAMP: 1234567890.0,
        }

        zmq_message = client._convert_from_router_format(router_message)

        assert zmq_message.message_type == MessageType.HEARTBEAT
        assert zmq_message.data is None
        assert zmq_message.client_id is None
        assert zmq_message.request_id is None
        assert zmq_message.timestamp == 1234567890.0

    def test_convert_from_router_format_unknown_message_type(self):
        """Test converting RouterConstants with unknown message type."""
        client = MQClient(
            router_address=self.router_address,
            client_type=self.client_type,
            client_id=self.client_id,
        )

        router_message = {
            RouterConstants.SENDER: RouterConstants.HYDRA_SERVER,
            RouterConstants.ELEM: "UnknownMessageType",
            RouterConstants.TIMESTAMP: 1234567890.0,
        }

        with pytest.raises(MessageFormatError):
            client._convert_from_router_format(router_message)

    @patch("hydra_router.mq_client.zmq.asyncio.Context")
    async def test_send_message_not_connected(self, mock_context):
        """Test sending message when not connected."""
        client = MQClient(
            router_address=self.router_address,
            client_type=self.client_type,
            client_id=self.client_id,
        )

        message = ZMQMessage(MessageType.HEARTBEAT)

        with pytest.raises(ConnectionError):
            await client.send_message(message)

    @patch("hydra_router.mq_client.zmq.asyncio.Context")
    async def test_register_message_handler(self, mock_context):
        """Test registering message handler."""
        client = MQClient(client_id=self.client_id, client_type=self.client_type)

        handler = AsyncMock()
        client.register_message_handler(MessageType.SQUARE_RESPONSE, handler)

        assert MessageType.SQUARE_RESPONSE in client.message_handlers
        assert client.message_handlers[MessageType.SQUARE_RESPONSE] == handler

    @patch("hydra_router.mq_client.zmq.asyncio.Context")
    async def test_unregister_message_handler(self, mock_context):
        """Test unregistering message handler."""
        client = MQClient(client_id=self.client_id, client_type=self.client_type)

        handler = AsyncMock()
        client.register_message_handler(MessageType.SQUARE_RESPONSE, handler)
        client.unregister_message_handler(MessageType.SQUARE_RESPONSE)

        assert MessageType.SQUARE_RESPONSE not in client.message_handlers

    def test_create_heartbeat_message(self):
        """Test creating heartbeat message."""
        client = MQClient(client_id=self.client_id, client_type=self.client_type)

        heartbeat = client._create_heartbeat_message()

        assert heartbeat.message_type == MessageType.HEARTBEAT
        assert heartbeat.client_id == self.client_id
        assert heartbeat.data is None
        assert heartbeat.request_id is None

    @patch("hydra_router.mq_client.zmq.asyncio.Context")
    async def test_context_manager(self, mock_context):
        """Test using MQClient as context manager."""
        mock_context_instance = Mock()
        mock_socket_instance = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket_instance

        async with MQClient(
            self.client_id, self.client_type, self.router_address
        ) as client:
            assert client.connected

        # Should be disconnected after exiting context
        assert not client.connected
