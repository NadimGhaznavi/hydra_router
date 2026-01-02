"""
Unit tests for custom exceptions module.

Tests the custom exception hierarchy and error handling
functionality provided by the exceptions module.
"""

import pytest

from hydra_router.exceptions import (
    ClientRegistrationError,
    ConfigurationError,
    ConnectionError,
    HydraRouterError,
    MessageFormatError,
    MessageRoutingError,
    MessageValidationError,
    ServerNotAvailableError,
    TimeoutError,
    create_connection_error,
    create_timeout_error,
    create_validation_error,
)


class TestHydraRouterError:
    """Test the base HydraRouterError exception."""

    def test_base_exception_creation(self):
        """Test creating base exception with message."""
        error = HydraRouterError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_base_exception_with_context(self):
        """Test creating base exception with context."""
        context = {"key": "value", "number": 123}
        error = HydraRouterError("Test error", context=context)
        assert "Test error" in str(error)
        assert error.context == context

    def test_base_exception_without_context(self):
        """Test creating base exception without context."""
        error = HydraRouterError("Test error")
        assert error.context == {}


class TestMessageValidationError:
    """Test MessageValidationError exception."""

    def test_validation_error_creation(self):
        """Test creating validation error."""
        error = MessageValidationError("Invalid message format")
        assert str(error) == "Invalid message format"
        assert isinstance(error, HydraRouterError)

    def test_validation_error_with_message_context(self):
        """Test creating validation error with message context."""
        invalid_message = {"sender": "invalid"}
        error = MessageValidationError(
            "Invalid format", invalid_message=invalid_message
        )
        assert error.invalid_message == invalid_message

    def test_validation_error_with_field_name(self):
        """Test creating validation error with field name."""
        error = MessageValidationError("Invalid field", field_name="sender")
        assert error.field_name == "sender"


class TestConnectionError:
    """Test ConnectionError exception."""

    def test_connection_error_creation(self):
        """Test creating connection error."""
        error = ConnectionError("Connection failed")
        assert str(error) == "Connection failed"
        assert isinstance(error, HydraRouterError)

    def test_connection_error_with_address(self):
        """Test creating connection error with address."""
        error = ConnectionError("Connection failed", address="tcp://localhost:5556")
        assert error.address == "tcp://localhost:5556"

    def test_connection_error_with_port(self):
        """Test creating connection error with port."""
        error = ConnectionError("Connection failed", port=5556)
        assert error.port == 5556


class TestClientRegistrationError:
    """Test ClientRegistrationError exception."""

    def test_client_registration_error_creation(self):
        """Test creating client registration error."""
        error = ClientRegistrationError("Registration failed")
        assert str(error) == "Registration failed"
        assert isinstance(error, HydraRouterError)

    def test_client_registration_error_with_client_id(self):
        """Test creating client registration error with client ID."""
        error = ClientRegistrationError("Registration failed", client_id="client-123")
        assert error.client_id == "client-123"

    def test_client_registration_error_with_client_type(self):
        """Test creating client registration error with client type."""
        error = ClientRegistrationError(
            "Registration failed", client_type="HydraClient"
        )
        assert error.client_type == "HydraClient"


class TestMessageRoutingError:
    """Test MessageRoutingError exception."""

    def test_routing_error_creation(self):
        """Test creating routing error."""
        error = MessageRoutingError("Routing failed")
        assert str(error) == "Routing failed"
        assert isinstance(error, HydraRouterError)

    def test_routing_error_with_target_client(self):
        """Test creating routing error with target client."""
        error = MessageRoutingError("Routing failed", target_client="client-123")
        assert error.target_client == "client-123"

    def test_routing_error_with_message_type(self):
        """Test creating routing error with message type."""
        error = MessageRoutingError("Routing failed", message_type="SquareRequest")
        assert error.message_type == "SquareRequest"

    def test_routing_error_with_source_client(self):
        """Test creating routing error with source client."""
        error = MessageRoutingError("Routing failed", source_client="client-456")
        assert error.source_client == "client-456"


class TestTimeoutError:
    """Test TimeoutError exception."""

    def test_timeout_error_creation(self):
        """Test creating timeout error."""
        error = TimeoutError("Operation timed out")
        assert str(error) == "Operation timed out"
        assert isinstance(error, HydraRouterError)

    def test_timeout_error_with_timeout_value(self):
        """Test creating timeout error with timeout value."""
        error = TimeoutError("Operation timed out", timeout_duration=30.0)
        assert error.timeout_duration == 30.0

    def test_timeout_error_with_operation(self):
        """Test creating timeout error with operation name."""
        error = TimeoutError("Operation timed out", operation="send_message")
        assert error.operation == "send_message"


class TestConfigurationError:
    """Test ConfigurationError exception."""

    def test_configuration_error_creation(self):
        """Test creating configuration error."""
        error = ConfigurationError("Invalid configuration")
        assert str(error) == "Invalid configuration"
        assert isinstance(error, HydraRouterError)

    def test_configuration_error_with_config_key(self):
        """Test creating configuration error with config key."""
        error = ConfigurationError("Invalid value", config_key="router_port")
        assert error.config_key == "router_port"

    def test_configuration_error_with_config_value(self):
        """Test creating configuration error with config value."""
        error = ConfigurationError("Invalid value", config_value="invalid_port")
        assert error.config_value == "invalid_port"


class TestMessageFormatError:
    """Test MessageFormatError exception."""

    def test_format_error_creation(self):
        """Test creating format error."""
        error = MessageFormatError("Format conversion failed")
        assert str(error) == "Format conversion failed"
        assert isinstance(error, HydraRouterError)

    def test_format_error_with_source_format(self):
        """Test creating format error with source format."""
        error = MessageFormatError("Conversion failed", source_format="ZMQMessage")
        assert error.source_format == "ZMQMessage"

    def test_format_error_with_target_format(self):
        """Test creating format error with target format."""
        error = MessageFormatError("Conversion failed", target_format="DRouter")
        assert error.target_format == "DRouter"


class TestServerNotAvailableError:
    """Test ServerNotAvailableError exception."""

    def test_server_not_available_error_creation(self):
        """Test creating server not available error."""
        error = ServerNotAvailableError("No server connected")
        assert "No server connected" in str(error)
        assert isinstance(error, HydraRouterError)

    def test_server_not_available_error_with_requested_operation(self):
        """Test creating server not available error with operation."""
        error = ServerNotAvailableError(
            "No server", client_id="client-123", message_type="square_calculation"
        )
        assert error.source_client == "client-123"
        assert error.message_type == "square_calculation"


class TestConvenienceFunctions:
    """Test convenience functions for creating exceptions."""

    def test_create_validation_error(self):
        """Test create_validation_error convenience function."""
        message = {"invalid": "format"}
        error = create_validation_error("sender", "string", "integer", message)

        assert isinstance(error, MessageValidationError)
        assert "sender" in str(error)
        assert error.invalid_message == message
        assert error.field_name == "sender"

    def test_create_connection_error(self):
        """Test create_connection_error convenience function."""
        error = create_connection_error("localhost", 5556)

        assert isinstance(error, ConnectionError)
        assert "localhost" in str(error)
        assert error.address == "localhost"
        assert error.port == 5556

    def test_create_timeout_error(self):
        """Test create_timeout_error convenience function."""
        error = create_timeout_error("send_message", 30.0, 35.0)

        assert isinstance(error, TimeoutError)
        assert "send_message" in str(error)
        assert error.operation == "send_message"
        assert error.timeout_duration == 30.0


class TestExceptionInheritance:
    """Test exception inheritance hierarchy."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from HydraRouterError."""
        exception_classes = [
            MessageValidationError,
            ConnectionError,
            ClientRegistrationError,
            MessageRoutingError,
            TimeoutError,
            ConfigurationError,
            MessageFormatError,
            ServerNotAvailableError,
        ]

        for exception_class in exception_classes:
            error = exception_class("Test message")
            assert isinstance(error, HydraRouterError)
            assert isinstance(error, Exception)

    def test_exception_context_inheritance(self):
        """Test that all exceptions support context parameter."""
        exception_classes_and_params = [
            (MessageValidationError, ("Test message",)),
            (ConnectionError, ("Test message",)),
            (ClientRegistrationError, ("Test message",)),
            (MessageRoutingError, ("Test message",)),
            (TimeoutError, ("Test message",)),
            (ConfigurationError, ("Test message",)),
            (MessageFormatError, ("Test message",)),
            (ServerNotAvailableError, ("Test message",)),
        ]

        for exception_class, params in exception_classes_and_params:
            error = exception_class(*params)
            assert hasattr(error, "context")
            assert isinstance(error.context, dict)
