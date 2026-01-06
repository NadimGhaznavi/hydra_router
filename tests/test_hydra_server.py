# tests/test_hydra_server.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

"""Unit tests for HydraServer abstract base class."""

import pytest
from unittest.mock import patch

from hydra_router.server.HydraServer import HydraServer
from hydra_router.constants.DHydra import DHydraServerDef


class ConcreteHydraServer(HydraServer):
    """Concrete test implementation of HydraServer for testing."""

    def handle_message(self, message: bytes) -> bytes:
        """Test implementation that echoes the message."""
        return b"Echo: " + message

    def run(self) -> None:
        """Test implementation of abstract run method."""
        self.start()


class TestHydraServer:
    """Test cases for HydraServer abstract base class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that HydraServer cannot be instantiated directly."""
        with pytest.raises(TypeError):
            HydraServer()

    @patch("hydra_router.server.HydraServer.HydraServer._setup_socket")
    def test_init_with_defaults(self, mock_setup):
        """Test HydraServer initialization with default parameters."""
        server = ConcreteHydraServer()

        assert server.address == "*"
        assert server.port == DHydraServerDef.PORT
        assert server.context is None
        assert server.socket is None

    @patch("hydra_router.server.HydraServer.HydraServer._setup_socket")
    def test_init_with_custom_parameters(self, mock_setup):
        """Test HydraServer initialization with custom parameters."""
        address = "localhost"
        port = 8080
        server_id = "TestServer"

        server = ConcreteHydraServer(address=address, port=port, server_id=server_id)

        assert server.address == address
        assert server.port == port

    def test_handle_message_implementation(self):
        """Test that handle_message is properly implemented."""
        with patch("hydra_router.server.HydraServer.HydraServer._setup_socket"):
            server = ConcreteHydraServer()
            result = server.handle_message(b"test")
            assert result == b"Echo: test"

    def test_abstract_methods_exist(self):
        """Test that abstract methods are properly defined."""
        # Verify that ConcreteHydraServer implements both abstract methods
        with patch("hydra_router.server.HydraServer.HydraServer._setup_socket"):
            server = ConcreteHydraServer()

            # Should not raise an error since we implemented them
            result = server.handle_message(b"test")
            assert result == b"Echo: test"

            # Mock start method to avoid actual server loop
            with patch.object(server, "start"):
                server.run()


if __name__ == "__main__":
    pytest.main([__file__])
