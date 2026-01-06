# tests/test_hydra_client_ping.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

"""Unit tests for HydraClientPing class."""

import json
import pytest
from unittest.mock import patch

from hydra_router.client.HydraClientPing import HydraClientPing
from hydra_router.constants.DHydra import DHydraServerDef
from hydra_router.utils.HydraMsg import HydraMsg


class TestHydraClientPing:
    """Test cases for HydraClientPing class."""

    @patch("hydra_router.client.HydraClient.HydraClient._setup_socket")
    def test_init_with_defaults(self, mock_setup):
        """Test HydraClientPing initialization with default parameters."""
        client = HydraClientPing()

        assert client._server_hostname == DHydraServerDef.HOSTNAME
        assert client._server_port == DHydraServerDef.PORT
        assert client.ping_count == 1
        assert client.ping_interval == 1.0
        assert client.message_payload == "ping"
        assert client.sent_pings == 0
        assert client.received_pongs == 0

    @patch("hydra_router.client.HydraClient.HydraClient._setup_socket")
    def test_init_with_custom_parameters(self, mock_setup):
        """Test HydraClientPing initialization with custom parameters."""
        hostname = "test.example.com"
        port = 9000
        count = 5
        interval = 0.5
        payload = "custom_ping"

        client = HydraClientPing(
            server_hostname=hostname,
            server_port=port,
            ping_count=count,
            ping_interval=interval,
            message_payload=payload,
        )

        assert client._server_hostname == hostname
        assert client._server_port == port
        assert client.ping_count == count
        assert client.ping_interval == interval
        assert client.message_payload == payload

    @patch("hydra_router.client.HydraClient.HydraClient._setup_socket")
    def test_create_ping_message(self, mock_setup):
        """Test creation of structured ping messages."""
        client = HydraClientPing(message_payload="test_message")

        sequence = 42
        ping_msg = client.create_ping_message(sequence)

        assert isinstance(ping_msg, HydraMsg)
        assert ping_msg._sender == "HydraPingClient"
        assert ping_msg._target == "HydraPongServer"
        assert ping_msg._method == "ping"

        # Parse payload
        payload_data = json.loads(ping_msg._payload)
        assert payload_data["sequence"] == sequence
        assert payload_data["message"] == "test_message"
        assert "timestamp" in payload_data

    @patch("hydra_router.client.HydraClient.HydraClient._setup_socket")
    def test_parse_pong_message_success(self, mock_setup):
        """Test successful parsing of pong response."""
        client = HydraClientPing()

        # Mock valid pong response
        pong_data = {
            "sender": "HydraPongServer",
            "method": "pong",
            "payload": json.dumps({"original_sequence": 1, "pong_message": "pong"}),
        }
        pong_bytes = json.dumps(pong_data).encode("utf-8")

        result = client.parse_pong_message(pong_bytes)

        assert result == pong_data
        assert "error" not in result

    @patch("hydra_router.client.HydraClient.HydraClient._setup_socket")
    def test_parse_pong_message_invalid_json(self, mock_setup):
        """Test parsing of invalid pong response."""
        client = HydraClientPing()

        # Invalid JSON
        invalid_bytes = b"invalid json data"

        result = client.parse_pong_message(invalid_bytes)

        assert "error" in result
        assert result["error"] == "Invalid response format"
        assert "raw" in result

    @patch("hydra_router.client.HydraClient.HydraClient._setup_socket")
    def test_success_rate_calculation(self, mock_setup):
        """Test success rate calculation in various scenarios."""
        client = HydraClientPing()

        # Test cases: (sent, received, expected_rate)
        test_cases = [
            (0, 0, 0),  # No pings sent
            (5, 5, 100.0),  # All successful
            (10, 7, 70.0),  # Partial success
            (3, 0, 0.0),  # All failed
        ]

        for sent, received, expected_rate in test_cases:
            client.sent_pings = sent
            client.received_pongs = received

            if sent > 0:
                actual_rate = (received / sent) * 100
            else:
                actual_rate = 0

            assert actual_rate == expected_rate


if __name__ == "__main__":
    pytest.main([__file__])
