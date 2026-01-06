# tests/test_hydra_server_pong.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

"""Unit tests for HydraServerPong class."""

import json
import pytest
from unittest.mock import patch

from hydra_router.server.HydraServerPong import HydraServerPong
from hydra_router.constants.DHydra import DHydraServerDef
from hydra_router.utils.HydraMsg import HydraMsg


class TestHydraServerPong:
    """Test cases for HydraServerPong class."""

    @patch("hydra_router.server.HydraServer.HydraServer._setup_socket")
    def test_init_with_defaults(self, mock_setup):
        """Test HydraServerPong initialization with default parameters."""
        server = HydraServerPong()

        assert server.address == "*"
        assert server.port == DHydraServerDef.PORT
        assert server.response_delay == 0.0
        assert server.ping_count == 0
        assert server.pong_count == 0

    @patch("hydra_router.server.HydraServer.HydraServer._setup_socket")
    def test_init_with_custom_parameters(self, mock_setup):
        """Test HydraServerPong initialization with custom parameters."""
        address = "localhost"
        port = 9000
        delay = 0.1

        server = HydraServerPong(address=address, port=port, response_delay=delay)

        assert server.address == address
        assert server.port == port
        assert server.response_delay == delay

    @patch("hydra_router.server.HydraServer.HydraServer._setup_socket")
    def test_parse_ping_message_success(self, mock_setup):
        """Test successful parsing of ping message."""
        server = HydraServerPong()

        # Mock valid ping message
        ping_data = {
            "sender": "HydraPingClient",
            "method": "ping",
            "payload": json.dumps({"sequence": 1, "message": "test"}),
        }
        ping_bytes = json.dumps(ping_data).encode("utf-8")

        result = server.parse_ping_message(ping_bytes)

        assert result == ping_data
        assert "error" not in result

    @patch("hydra_router.server.HydraServer.HydraServer._setup_socket")
    def test_parse_ping_message_invalid_json(self, mock_setup):
        """Test parsing of invalid ping message."""
        server = HydraServerPong()

        # Invalid JSON
        invalid_bytes = b"invalid json data"

        result = server.parse_ping_message(invalid_bytes)

        assert "error" in result
        assert result["error"] == "Invalid message format"
        assert "raw" in result

    @patch("hydra_router.server.HydraServer.HydraServer._setup_socket")
    @patch("time.time")
    def test_create_pong_response(self, mock_time, mock_setup):
        """Test creation of structured pong response."""
        mock_time.return_value = 2000.0

        server = HydraServerPong()

        # Mock ping data
        ping_data = {
            "sender": "HydraPingClient",
            "method": "ping",
            "payload": json.dumps(
                {"sequence": 42, "message": "test_ping", "timestamp": 1000.0}
            ),
        }

        pong_msg = server.create_pong_response(ping_data)

        assert isinstance(pong_msg, HydraMsg)
        assert pong_msg._sender == "HydraPongServer"
        assert pong_msg._target == "HydraPingClient"
        assert pong_msg._method == "pong"

        # Parse pong payload
        pong_payload = json.loads(pong_msg._payload)
        assert pong_payload["original_sequence"] == 42
        assert pong_payload["original_message"] == "test_ping"
        assert pong_payload["original_timestamp"] == 1000.0
        assert pong_payload["pong_message"] == "pong"
        assert pong_payload["pong_timestamp"] == 2000.0
        assert pong_payload["server_id"] == "HydraPongServer"

    @patch("hydra_router.server.HydraServer.HydraServer._setup_socket")
    @patch("time.time")
    def test_create_error_response(self, mock_time, mock_setup):
        """Test creation of error response."""
        mock_time.return_value = 3000.0

        server = HydraServerPong()

        error_msg = "Test error message"
        error_bytes = server.create_error_response(error_msg)

        error_data = json.loads(error_bytes.decode("utf-8"))
        assert error_data["error"] == error_msg
        assert error_data["server_id"] == "HydraPongServer"
        assert error_data["timestamp"] == 3000.0

    @patch("hydra_router.server.HydraServer.HydraServer._setup_socket")
    def test_handle_message_valid_ping(self, mock_setup):
        """Test handling of valid ping message."""
        server = HydraServerPong()

        # Create valid ping message
        ping_data = {
            "sender": "HydraPingClient",
            "method": "ping",
            "payload": json.dumps({"sequence": 1, "message": "test"}),
        }
        ping_bytes = json.dumps(ping_data).encode("utf-8")

        # Handle message
        response_bytes = server.handle_message(ping_bytes)

        # Verify response
        response_data = json.loads(response_bytes.decode("utf-8"))
        assert response_data["sender"] == "HydraPongServer"
        assert response_data["target"] == "HydraPingClient"
        assert response_data["method"] == "pong"

        # Verify counters
        assert server.ping_count == 1
        assert server.pong_count == 1

    @patch("hydra_router.server.HydraServer.HydraServer._setup_socket")
    def test_handle_message_invalid_method(self, mock_setup):
        """Test handling of message with invalid method."""
        server = HydraServerPong()

        # Create message with invalid method
        invalid_data = {
            "sender": "TestClient",
            "method": "invalid_method",
            "payload": json.dumps({"test": "data"}),
        }
        invalid_bytes = json.dumps(invalid_data).encode("utf-8")

        # Handle message
        response_bytes = server.handle_message(invalid_bytes)

        # Verify error response
        response_data = json.loads(response_bytes.decode("utf-8"))
        assert "error" in response_data
        assert "Unsupported method: invalid_method" in response_data["error"]

        # Verify counters
        assert server.ping_count == 1
        assert server.pong_count == 0

    @patch("hydra_router.server.HydraServer.HydraServer._setup_socket")
    def test_handle_message_parse_error(self, mock_setup):
        """Test handling of unparseable message."""
        server = HydraServerPong()

        # Invalid JSON message
        invalid_bytes = b"not valid json"

        # Handle message
        response_bytes = server.handle_message(invalid_bytes)

        # Verify error response
        response_data = json.loads(response_bytes.decode("utf-8"))
        assert "error" in response_data
        assert "Invalid message format" in response_data["error"]

        # Verify counters
        assert server.ping_count == 1
        assert server.pong_count == 0


if __name__ == "__main__":
    pytest.main([__file__])
