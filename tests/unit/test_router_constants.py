"""
Unit tests for DRouter module.

Tests the constants, validation helpers, and utility methods
provided by the DRouter class.
"""

from hydra_router.constants.DRouter import DRouter


class TestDRouter:
    """Test DRouter class and its constants."""

    def test_client_types_defined(self):
        """Test that all client types are properly defined."""
        assert hasattr(DRouter, "HYDRA_CLIENT")
        assert hasattr(DRouter, "HYDRA_SERVER")
        assert hasattr(DRouter, "SIMPLE_CLIENT")
        assert hasattr(DRouter, "SIMPLE_SERVER")
        assert hasattr(DRouter, "HYDRA_ROUTER")

    def test_message_fields_defined(self):
        """Test that all message field constants are defined."""
        assert hasattr(DRouter, "SENDER")
        assert hasattr(DRouter, "ELEM")
        assert hasattr(DRouter, "DATA")
        assert hasattr(DRouter, "CLIENT_ID")
        assert hasattr(DRouter, "TIMESTAMP")
        assert hasattr(DRouter, "REQUEST_ID")

    def test_message_types_defined(self):
        """Test that all message type constants are defined."""
        assert hasattr(DRouter, "HEARTBEAT")
        assert hasattr(DRouter, "ERROR")
        assert hasattr(DRouter, "CLIENT_REGISTRY_REQUEST")
        assert hasattr(DRouter, "CLIENT_REGISTRY_RESPONSE")
        assert hasattr(DRouter, "SQUARE_REQUEST")
        assert hasattr(DRouter, "SQUARE_RESPONSE")

    def test_network_constants_defined(self):
        """Test that network configuration constants are defined."""
        assert hasattr(DRouter, "DEFAULT_ROUTER_ADDRESS")
        assert hasattr(DRouter, "DEFAULT_ROUTER_PORT")
        assert hasattr(DRouter, "DEFAULT_CLIENT_TIMEOUT")

    def test_error_constants_defined(self):
        """Test that error constants are defined."""
        assert hasattr(DRouter, "NO_SERVER_CONNECTED")

    def test_valid_client_types_list(self):
        """Test that VALID_CLIENT_TYPES contains all expected client types."""
        expected_types = {
            DRouter.HYDRA_CLIENT,
            DRouter.HYDRA_SERVER,
            DRouter.HYDRA_ROUTER,
            DRouter.SIMPLE_CLIENT,
            DRouter.SIMPLE_SERVER,
        }
        assert set(DRouter.VALID_CLIENT_TYPES) == expected_types

    def test_is_valid_client_type(self):
        """Test client type validation method."""
        # Valid client types
        assert DRouter.is_valid_client_type(DRouter.HYDRA_CLIENT)
        assert DRouter.is_valid_client_type(DRouter.HYDRA_SERVER)
        assert DRouter.is_valid_client_type(DRouter.SIMPLE_CLIENT)
        assert DRouter.is_valid_client_type(DRouter.SIMPLE_SERVER)

        # Invalid client types
        assert not DRouter.is_valid_client_type("InvalidClient")
        assert not DRouter.is_valid_client_type("")
        assert not DRouter.is_valid_client_type(None)

    def test_is_system_message(self):
        """Test system message classification method."""
        # System messages (based on actual implementation)
        assert DRouter.is_system_message(DRouter.HEARTBEAT)
        assert DRouter.is_system_message(DRouter.ERROR)
        assert DRouter.is_system_message(DRouter.STATUS)

        # Non-system messages
        assert not DRouter.is_system_message(DRouter.CLIENT_REGISTRY_REQUEST)
        assert not DRouter.is_system_message(DRouter.CLIENT_REGISTRY_RESPONSE)
        assert not DRouter.is_system_message(DRouter.SQUARE_REQUEST)
        assert not DRouter.is_system_message(DRouter.SQUARE_RESPONSE)

        # Invalid messages
        assert not DRouter.is_system_message("InvalidMessage")

    def test_constants_are_strings(self):
        """Test that all constants are strings."""
        string_constants = [
            DRouter.HYDRA_CLIENT,
            DRouter.HYDRA_SERVER,
            DRouter.SIMPLE_CLIENT,
            DRouter.SIMPLE_SERVER,
            DRouter.HYDRA_ROUTER,
            DRouter.SENDER,
            DRouter.ELEM,
            DRouter.DATA,
            DRouter.CLIENT_ID,
            DRouter.TIMESTAMP,
            DRouter.REQUEST_ID,
            DRouter.HEARTBEAT,
            DRouter.ERROR,
            DRouter.CLIENT_REGISTRY_REQUEST,
            DRouter.CLIENT_REGISTRY_RESPONSE,
            DRouter.SQUARE_REQUEST,
            DRouter.SQUARE_RESPONSE,
            DRouter.DEFAULT_ROUTER_ADDRESS,
            DRouter.NO_SERVER_CONNECTED,
        ]

        for constant in string_constants:
            assert isinstance(constant, str)
            assert len(constant) > 0

    def test_numeric_constants(self):
        """Test that numeric constants have appropriate values."""
        assert isinstance(DRouter.DEFAULT_ROUTER_PORT, int)
        assert DRouter.DEFAULT_ROUTER_PORT > 0
        assert DRouter.DEFAULT_ROUTER_PORT < 65536

        assert isinstance(DRouter.DEFAULT_CLIENT_TIMEOUT, (int, float))
        assert DRouter.DEFAULT_CLIENT_TIMEOUT > 0

    def test_constants_uniqueness(self):
        """Test that all constants have unique values."""
        client_types = [
            DRouter.HYDRA_CLIENT,
            DRouter.HYDRA_SERVER,
            DRouter.SIMPLE_CLIENT,
            DRouter.SIMPLE_SERVER,
            DRouter.HYDRA_ROUTER,
        ]
        assert len(client_types) == len(set(client_types))

        message_fields = [
            DRouter.SENDER,
            DRouter.ELEM,
            DRouter.DATA,
            DRouter.CLIENT_ID,
            DRouter.TIMESTAMP,
            DRouter.REQUEST_ID,
        ]
        assert len(message_fields) == len(set(message_fields))

        message_types = [
            DRouter.HEARTBEAT,
            DRouter.ERROR,
            DRouter.CLIENT_REGISTRY_REQUEST,
            DRouter.CLIENT_REGISTRY_RESPONSE,
            DRouter.SQUARE_REQUEST,
            DRouter.SQUARE_RESPONSE,
        ]
        assert len(message_types) == len(set(message_types))

    def test_is_simulation_command(self):
        """Test simulation command classification method."""
        # Simulation commands
        assert DRouter.is_simulation_command(DRouter.START_SIMULATION)
        assert DRouter.is_simulation_command(DRouter.STOP_SIMULATION)
        assert DRouter.is_simulation_command(DRouter.PAUSE_SIMULATION)
        assert DRouter.is_simulation_command(DRouter.RESUME_SIMULATION)
        assert DRouter.is_simulation_command(DRouter.RESET_SIMULATION)
        assert DRouter.is_simulation_command(DRouter.GET_SIMULATION_STATUS)

        # Non-simulation commands
        assert not DRouter.is_simulation_command(DRouter.HEARTBEAT)
        assert not DRouter.is_simulation_command(DRouter.SQUARE_REQUEST)

        # Invalid commands
        assert not DRouter.is_simulation_command("InvalidCommand")

    def test_get_all_message_types(self):
        """Test getting all message types."""
        message_types = DRouter.get_all_message_types()
        assert isinstance(message_types, list)
        assert DRouter.HEARTBEAT in message_types
        assert DRouter.SQUARE_REQUEST in message_types
        assert DRouter.CLIENT_REGISTRY_REQUEST in message_types

    def test_get_required_fields(self):
        """Test getting required fields."""
        required_fields = DRouter.get_required_fields()
        assert isinstance(required_fields, list)
        assert DRouter.SENDER in required_fields
        assert DRouter.ELEM in required_fields

    def test_get_optional_fields(self):
        """Test getting optional fields."""
        optional_fields = DRouter.get_optional_fields()
        assert isinstance(optional_fields, list)
        assert DRouter.DATA in optional_fields
        assert DRouter.CLIENT_ID in optional_fields

    def test_get_all_fields(self):
        """Test getting all fields."""
        all_fields = DRouter.get_all_fields()
        assert isinstance(all_fields, list)
        assert DRouter.SENDER in all_fields
        assert DRouter.DATA in all_fields
