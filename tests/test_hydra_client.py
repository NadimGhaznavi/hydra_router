# tests/test_hydra_client.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

"""Unit tests for HydraClient class."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import zmq

from hydra_router.client.HydraClient import HydraClient
from hydra_router.constants.DHydra import DHydraClientMsg, DHydraServerDef


class TestHydraClient:
    """Test cases for HydraClient class."""

    def test_init_with_defaults(self):
        """Test HydraClient initialization with default parameters."""
        with patch("hydra_router.client.HydraClient.HydraClient._setup_socket"):
            client = HydraClient()

            assert client._server_hostname == DHydraServerDef.HOSTNAME
            assert client._server_port == DHydraServerDef.PORT
            assert (
                client.server_address
                == f"tcp://{DHydraServerDef.HOSTNAME}:{DHydraServerDef.PORT}"
            )

    def test_init_with_custom_parameters(self):
        """Test HydraClient initialization with custom parameters."""
        hostname = "192.168.1.100"
        port = 8080

        with patch("hydra_router.client.HydraClient.HydraClient._setup_socket"):
            client = HydraClient(server_hostname=hostname, server_port=port)

            assert client._server_hostname == hostname
            assert client._server_port == port
            assert client.server_address == f"tcp://{hostname}:{port}"

    def test_init_with_partial_parameters(self):
        """Test HydraClient initialization with only hostname specified."""
        hostname = "example.com"

        with patch("hydra_router.client.HydraClient.HydraClient._setup_socket"):
            client = HydraClient(server_hostname=hostname)

            assert client._server_hostname == hostname
            assert client._server_port == DHydraServerDef.PORT
            assert client.server_address == f"tcp://{hostname}:{DHydraServerDef.PORT}"

    @patch("zmq.Context")
    @patch("builtins.print")
    def test_setup_socket_success(self, mock_print, mock_context_class):
        """Test successful socket setup."""
        # Mock ZMQ context and socket
        mock_context = Mock()
        mock_socket = Mock()
        mock_context_class.return_value = mock_context
        mock_context.socket.return_value = mock_socket

        client = HydraClient()

        # Verify ZMQ setup calls
        mock_context_class.assert_called_once()
        mock_context.socket.assert_called_once_with(zmq.REQ)
        mock_socket.connect.assert_called_once_with(client.server_address)

        # Verify success message
        expected_message = DHydraClientMsg.CONNECTED.format(
            server_address=client.server_address
        )
        mock_print.assert_called_with(expected_message)

        # Verify client state
        assert client.context == mock_context
        assert client.socket == mock_socket

    @patch("zmq.Context")
    @patch("builtins.print")
    @patch("builtins.exit")
    def test_setup_socket_failure(self, mock_exit, mock_print, mock_context_class):
        """Test socket setup failure handling."""
        # Mock ZMQ context to raise exception
        mock_context_class.side_effect = Exception("Connection failed")

        HydraClient()

        # Verify error handling
        expected_error = DHydraClientMsg.ERROR.format(e="Connection failed")
        mock_print.assert_called_with(expected_error)
        mock_exit.assert_called_once_with(1)

    @patch("hydra_router.client.HydraClient.HydraClient._setup_socket")
    @patch("builtins.print")
    def test_send_message_success(self, mock_print, mock_setup):
        """Test successful message sending and receiving."""
        client = HydraClient()

        # Mock socket
        mock_socket = Mock()
        client.socket = mock_socket

        # Mock response
        test_message = b"Hello"
        test_response = b"World"
        mock_socket.recv.return_value = test_response

        # Send message
        response = client.send_message(test_message)

        # Verify socket calls
        mock_socket.send.assert_called_once_with(test_message)
        mock_socket.recv.assert_called_once()

        # Verify print calls
        sending_msg = DHydraClientMsg.SENDING.format(message=test_message)
        received_msg = DHydraClientMsg.RECEIVED.format(response=test_response)
        mock_print.assert_any_call(sending_msg)
        mock_print.assert_any_call(received_msg)

        # Verify response
        assert response == test_response

    @patch("hydra_router.client.HydraClient.HydraClient._setup_socket")
    @patch("builtins.print")
    @patch("builtins.exit")
    def test_send_message_no_socket(self, mock_exit, mock_print, mock_setup):
        """Test send_message when socket is None."""
        client = HydraClient()
        client.socket = None

        test_message = b"Hello"

        # Send message should fail
        client.send_message(test_message)

        # Verify error handling
        expected_error = DHydraClientMsg.ERROR.format(e="Socket not initialized")
        mock_print.assert_called_with(expected_error)
        mock_exit.assert_called_once_with(1)

    @patch("hydra_router.client.HydraClient.HydraClient._setup_socket")
    @patch("builtins.print")
    @patch("builtins.exit")
    def test_send_message_socket_error(self, mock_exit, mock_print, mock_setup):
        """Test send_message when socket operation fails."""
        client = HydraClient()

        # Mock socket that raises exception
        mock_socket = Mock()
        mock_socket.send.side_effect = Exception("Network error")
        client.socket = mock_socket

        test_message = b"Hello"

        # Send message should fail
        client.send_message(test_message)

        # Verify error handling
        expected_error = DHydraClientMsg.ERROR.format(e="Network error")
        mock_print.assert_called_with(expected_error)
        mock_exit.assert_called_once_with(1)

    @patch("hydra_router.client.HydraClient.HydraClient._setup_socket")
    @patch("builtins.print")
    def test_cleanup_success(self, mock_print, mock_setup):
        """Test successful cleanup of resources."""
        client = HydraClient()

        # Mock socket and context
        mock_socket = Mock()
        mock_context = Mock()
        client.socket = mock_socket
        client.context = mock_context

        # Cleanup
        client._cleanup()

        # Verify cleanup calls
        mock_socket.close.assert_called_once()
        mock_context.term.assert_called_once()
        mock_print.assert_called_with(DHydraClientMsg.CLEANUP)

    @patch("hydra_router.client.HydraClient.HydraClient._setup_socket")
    @patch("builtins.print")
    def test_cleanup_with_none_resources(self, mock_print, mock_setup):
        """Test cleanup when socket and context are None."""
        client = HydraClient()
        client.socket = None
        client.context = None

        # Cleanup should not raise errors
        client._cleanup()

        # Should still print cleanup message
        mock_print.assert_called_with(DHydraClientMsg.CLEANUP)

    @patch("hydra_router.client.HydraClient.HydraClient._setup_socket")
    def test_server_address_formatting(self, mock_setup):
        """Test server address formatting with various inputs."""
        test_cases = [
            ("localhost", 5757, "tcp://localhost:5757"),
            ("192.168.1.1", 8080, "tcp://192.168.1.1:8080"),
            ("example.com", 9000, "tcp://example.com:9000"),
        ]

        for hostname, port, expected_address in test_cases:
            client = HydraClient(server_hostname=hostname, server_port=port)
            assert client.server_address == expected_address

    @patch("hydra_router.client.HydraClient.HydraClient._setup_socket")
    def test_message_types(self, mock_setup):
        """Test sending different types of byte messages."""
        client = HydraClient()

        # Mock socket
        mock_socket = Mock()
        client.socket = mock_socket

        test_messages = [
            b"Hello World",
            b"",  # Empty message
            b"\x00\x01\x02",  # Binary data
            "Unicode test: 你好".encode("utf-8"),  # Unicode
        ]

        for message in test_messages:
            mock_socket.reset_mock()
            mock_socket.recv.return_value = b"Response"

            with patch("builtins.print"):  # Suppress print output
                response = client.send_message(message)

            mock_socket.send.assert_called_once_with(message)
            assert response == b"Response"


class TestHydraClientIntegration:
    """Integration-style tests for HydraClient."""

    @patch("zmq.Context")
    @patch("builtins.print")
    def test_full_client_lifecycle(self, mock_print, mock_context_class):
        """Test complete client lifecycle: init -> send -> cleanup."""
        # Setup mocks
        mock_context = Mock()
        mock_socket = Mock()
        mock_context_class.return_value = mock_context
        mock_context.socket.return_value = mock_socket
        mock_socket.recv.return_value = b"Server Response"

        # Create client
        client = HydraClient(server_hostname="testhost", server_port=9999)

        # Send message
        response = client.send_message(b"Test Message")

        # Cleanup
        client._cleanup()

        # Verify full flow
        assert response == b"Server Response"
        mock_socket.send.assert_called_once_with(b"Test Message")
        mock_socket.close.assert_called_once()
        mock_context.term.assert_called_once()

        # Verify expected server address
        assert client.server_address == "tcp://testhost:9999"


if __name__ == "__main__":
    pytest.main([__file__])
