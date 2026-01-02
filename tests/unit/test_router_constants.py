"""
Unit tests for RouterConstants module.

Tests the constants, validation helpers, and utility methods
provided by the RouterConstants class.
"""

from hydra_router.router_constants import RouterConstants


class TestRouterConstants:
    """Test RouterConstants class and its constants."""

    def test_client_types_defined(self):
        """Test that all client types are properly defined."""
        assert hasattr(RouterConstants, "HYDRA_CLIENT")
        assert hasattr(RouterConstants, "HYDRA_SERVER")
        assert hasattr(RouterConstants, "SIMPLE_CLIENT")
        assert hasattr(RouterConstants, "SIMPLE_SERVER")
        assert hasattr(RouterConstants, "HYDRA_ROUTER")

    def test_message_fields_defined(self):
        """Test that all message field constants are defined."""
        assert hasattr(RouterConstants, "SENDER")
        assert hasattr(RouterConstants, "ELEM")
        assert hasattr(RouterConstants, "DATA")
        assert hasattr(RouterConstants, "CLIENT_ID")
        assert hasattr(RouterConstants, "TIMESTAMP")
        assert hasattr(RouterConstants, "REQUEST_ID")

    def test_message_types_defined(self):
        """Test that all message type constants are defined."""
        assert hasattr(RouterConstants, "HEARTBEAT")
        assert hasattr(RouterConstants, "ERROR")
        assert hasattr(RouterConstants, "CLIENT_REGISTRY_REQUEST")
        assert hasattr(RouterConstants, "CLIENT_REGISTRY_RESPONSE")
        assert hasattr(RouterConstants, "SQUARE_REQUEST")
        assert hasattr(RouterConstants, "SQUARE_RESPONSE")

    def test_network_constants_defined(self):
        """Test that network configuration constants are defined."""
        assert hasattr(RouterConstants, "DEFAULT_ROUTER_ADDRESS")
        assert hasattr(RouterConstants, "DEFAULT_ROUTER_PORT")
        assert hasattr(RouterConstants, "DEFAULT_CLIENT_TIMEOUT")

    def test_error_constants_defined(self):
        """Test that error constants are defined."""
        assert hasattr(RouterConstants, "NO_SERVER_CONNECTED")

    def test_valid_client_types_list(self):
        """Test that VALID_CLIENT_TYPES contains all expected client types."""
        expected_types = {
            RouterConstants.HYDRA_CLIENT,
            RouterConstants.HYDRA_SERVER,
            RouterConstants.HYDRA_ROUTER,
            RouterConstants.SIMPLE_CLIENT,
            RouterConstants.SIMPLE_SERVER,
        }
        assert set(RouterConstants.VALID_CLIENT_TYPES) == expected_types

    def test_is_valid_client_type(self):
        """Test client type validation method."""
        # Valid client types
        assert RouterConstants.is_valid_client_type(RouterConstants.HYDRA_CLIENT)
        assert RouterConstants.is_valid_client_type(RouterConstants.HYDRA_SERVER)
        assert RouterConstants.is_valid_client_type(RouterConstants.SIMPLE_CLIENT)
        assert RouterConstants.is_valid_client_type(RouterConstants.SIMPLE_SERVER)

        # Invalid client types
        assert not RouterConstants.is_valid_client_type("InvalidClient")
        assert not RouterConstants.is_valid_client_type("")
        assert not RouterConstants.is_valid_client_type(None)

    def test_is_system_message(self):
        """Test system message classification method."""
        # System messages (based on actual implementation)
        assert RouterConstants.is_system_message(RouterConstants.HEARTBEAT)
        assert RouterConstants.is_system_message(RouterConstants.ERROR)
        assert RouterConstants.is_system_message(RouterConstants.STATUS)

        # Non-system messages
        assert not RouterConstants.is_system_message(
            RouterConstants.CLIENT_REGISTRY_REQUEST
        )
        assert not RouterConstants.is_system_message(
            RouterConstants.CLIENT_REGISTRY_RESPONSE
        )
        assert not RouterConstants.is_system_message(RouterConstants.SQUARE_REQUEST)
        assert not RouterConstants.is_system_message(RouterConstants.SQUARE_RESPONSE)

        # Invalid messages
        assert not RouterConstants.is_system_message("InvalidMessage")

    def test_constants_are_strings(self):
        """Test that all constants are strings."""
        string_constants = [
            RouterConstants.HYDRA_CLIENT,
            RouterConstants.HYDRA_SERVER,
            RouterConstants.SIMPLE_CLIENT,
            RouterConstants.SIMPLE_SERVER,
            RouterConstants.HYDRA_ROUTER,
            RouterConstants.SENDER,
            RouterConstants.ELEM,
            RouterConstants.DATA,
            RouterConstants.CLIENT_ID,
            RouterConstants.TIMESTAMP,
            RouterConstants.REQUEST_ID,
            RouterConstants.HEARTBEAT,
            RouterConstants.ERROR,
            RouterConstants.CLIENT_REGISTRY_REQUEST,
            RouterConstants.CLIENT_REGISTRY_RESPONSE,
            RouterConstants.SQUARE_REQUEST,
            RouterConstants.SQUARE_RESPONSE,
            RouterConstants.DEFAULT_ROUTER_ADDRESS,
            RouterConstants.NO_SERVER_CONNECTED,
        ]

        for constant in string_constants:
            assert isinstance(constant, str)
            assert len(constant) > 0

    def test_numeric_constants(self):
        """Test that numeric constants have appropriate values."""
        assert isinstance(RouterConstants.DEFAULT_ROUTER_PORT, int)
        assert RouterConstants.DEFAULT_ROUTER_PORT > 0
        assert RouterConstants.DEFAULT_ROUTER_PORT < 65536

        assert isinstance(RouterConstants.DEFAULT_CLIENT_TIMEOUT, (int, float))
        assert RouterConstants.DEFAULT_CLIENT_TIMEOUT > 0

    def test_constants_uniqueness(self):
        """Test that all constants have unique values."""
        client_types = [
            RouterConstants.HYDRA_CLIENT,
            RouterConstants.HYDRA_SERVER,
            RouterConstants.SIMPLE_CLIENT,
            RouterConstants.SIMPLE_SERVER,
            RouterConstants.HYDRA_ROUTER,
        ]
        assert len(client_types) == len(set(client_types))

        message_fields = [
            RouterConstants.SENDER,
            RouterConstants.ELEM,
            RouterConstants.DATA,
            RouterConstants.CLIENT_ID,
            RouterConstants.TIMESTAMP,
            RouterConstants.REQUEST_ID,
        ]
        assert len(message_fields) == len(set(message_fields))

        message_types = [
            RouterConstants.HEARTBEAT,
            RouterConstants.ERROR,
            RouterConstants.CLIENT_REGISTRY_REQUEST,
            RouterConstants.CLIENT_REGISTRY_RESPONSE,
            RouterConstants.SQUARE_REQUEST,
            RouterConstants.SQUARE_RESPONSE,
        ]
        assert len(message_types) == len(set(message_types))

    def test_is_simulation_command(self):
        """Test simulation command classification method."""
        # Simulation commands
        assert RouterConstants.is_simulation_command(RouterConstants.START_SIMULATION)
        assert RouterConstants.is_simulation_command(RouterConstants.STOP_SIMULATION)
        assert RouterConstants.is_simulation_command(RouterConstants.PAUSE_SIMULATION)
        assert RouterConstants.is_simulation_command(RouterConstants.RESUME_SIMULATION)
        assert RouterConstants.is_simulation_command(RouterConstants.RESET_SIMULATION)
        assert RouterConstants.is_simulation_command(
            RouterConstants.GET_SIMULATION_STATUS
        )

        # Non-simulation commands
        assert not RouterConstants.is_simulation_command(RouterConstants.HEARTBEAT)
        assert not RouterConstants.is_simulation_command(RouterConstants.SQUARE_REQUEST)

        # Invalid commands
        assert not RouterConstants.is_simulation_command("InvalidCommand")

    def test_get_all_message_types(self):
        """Test getting all message types."""
        message_types = RouterConstants.get_all_message_types()
        assert isinstance(message_types, list)
        assert RouterConstants.HEARTBEAT in message_types
        assert RouterConstants.SQUARE_REQUEST in message_types
        assert RouterConstants.CLIENT_REGISTRY_REQUEST in message_types

    def test_get_required_fields(self):
        """Test getting required fields."""
        required_fields = RouterConstants.get_required_fields()
        assert isinstance(required_fields, list)
        assert RouterConstants.SENDER in required_fields
        assert RouterConstants.ELEM in required_fields

    def test_get_optional_fields(self):
        """Test getting optional fields."""
        optional_fields = RouterConstants.get_optional_fields()
        assert isinstance(optional_fields, list)
        assert RouterConstants.DATA in optional_fields
        assert RouterConstants.CLIENT_ID in optional_fields

    def test_get_all_fields(self):
        """Test getting all fields."""
        all_fields = RouterConstants.get_all_fields()
        assert isinstance(all_fields, list)
        assert RouterConstants.SENDER in all_fields
        assert RouterConstants.DATA in all_fields
