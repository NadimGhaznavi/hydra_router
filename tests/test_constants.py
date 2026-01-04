"""Test constants module."""

import pytest
from hydra_router.constants.DHydra import (
    DHydra,
    DHydraClientMsg,
    DHydraServerDef,
    DHydraServerMsg,
)


class TestDHydra:
    """Test DHydra constants."""

    def test_version_exists(self):
        """Test that version constant exists and is a string."""
        assert isinstance(DHydra.VERSION, str)
        assert len(DHydra.VERSION) > 0


class TestDHydraServerDef:
    """Test DHydraServerDef constants."""

    def test_hostname_default(self):
        """Test hostname default value."""
        assert DHydraServerDef.HOSTNAME == "localhost"

    def test_port_default(self):
        """Test port default value."""
        assert isinstance(DHydraServerDef.PORT, int)
        assert DHydraServerDef.PORT > 0


class TestDHydraClientMsg:
    """Test DHydraClientMsg constants."""

    def test_messages_have_placeholders(self):
        """Test that messages contain format placeholders."""
        assert "{server_address}" in DHydraClientMsg.CONNECTED
        assert "{e}" in DHydraClientMsg.ERROR
        assert "{server_port}" in DHydraClientMsg.PORT_HELP

    def test_cleanup_message(self):
        """Test cleanup message."""
        assert "cleanup" in DHydraClientMsg.CLEANUP.lower()


class TestDHydraServerMsg:
    """Test DHydraServerMsg constants."""

    def test_messages_have_placeholders(self):
        """Test that messages contain format placeholders."""
        assert "{bind_address}" in DHydraServerMsg.BIND
        assert "{address}" in DHydraServerMsg.LOOP_UP
        assert "{port}" in DHydraServerMsg.LOOP_UP

    def test_help_messages(self):
        """Test help messages."""
        assert "address" in DHydraServerMsg.ADDRESS_HELP.lower()
        assert "port" in DHydraServerMsg.PORT_HELP.lower()
