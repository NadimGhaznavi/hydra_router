"""
Custom exceptions for the Hydra Router system.

This module provides a comprehensive exception hierarchy for all Hydra Router
components, enabling precise error handling and debugging capabilities.
"""

from typing import Any, Dict, Optional


class HydraRouterError(Exception):
    """
    Base exception for all Hydra Router errors.

    All Hydra Router exceptions inherit from this base class, allowing
    for comprehensive error handling at different levels of granularity.
    """

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize the base Hydra Router error.

        Args:
            message: Human-readable error message
            context: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} (Context: {context_str})"
        return self.message

    def add_context(self, key: str, value: Any) -> None:
        """
        Add additional context to the error.

        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value

    def get_context(self) -> Dict[str, Any]:
        """
        Get the error context dictionary.

        Returns:
            Dictionary containing error context
        """
        return self.context.copy()


class MessageValidationError(HydraRouterError):
    """
    Exception raised when message format validation fails.

    This exception is raised when messages don't conform to the expected
    RouterConstants format or contain invalid field values.
    """

    def __init__(
        self,
        message: str,
        invalid_message: Optional[Dict[str, Any]] = None,
        validation_details: Optional[str] = None,
        field_name: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_type: Optional[str] = None,
    ):
        """
        Initialize message validation error.

        Args:
            message: Human-readable error message
            invalid_message: The message that failed validation
            validation_details: Detailed validation error information
            field_name: Name of the field that failed validation
            expected_type: Expected type/format for the field
            actual_type: Actual type/format found
        """
        context = {}
        if invalid_message is not None:
            context["invalid_message"] = invalid_message
        if validation_details:
            context["validation_details"] = validation_details
        if field_name:
            context["field_name"] = field_name
        if expected_type:
            context["expected_type"] = expected_type
        if actual_type:
            context["actual_type"] = actual_type

        super().__init__(message, context)
        self.invalid_message = invalid_message
        self.validation_details = validation_details
        self.field_name = field_name
        self.expected_type = expected_type
        self.actual_type = actual_type


class ConnectionError(HydraRouterError):
    """
    Exception raised for network connection issues.

    This exception covers various connection-related problems including
    connection failures, timeouts, and network communication errors.
    """

    def __init__(
        self,
        message: str,
        address: Optional[str] = None,
        port: Optional[int] = None,
        timeout: Optional[float] = None,
        retry_count: Optional[int] = None,
        underlying_error: Optional[Exception] = None,
    ):
        """
        Initialize connection error.

        Args:
            message: Human-readable error message
            address: Network address that failed
            port: Network port that failed
            timeout: Timeout value used
            retry_count: Number of retries attempted
            underlying_error: The underlying exception that caused this error
        """
        context = {}
        if address:
            context["address"] = address
        if port:
            context["port"] = port
        if timeout:
            context["timeout"] = timeout
        if retry_count is not None:
            context["retry_count"] = retry_count
        if underlying_error:
            context["underlying_error"] = str(underlying_error)

        super().__init__(message, context)
        self.address = address
        self.port = port
        self.timeout = timeout
        self.retry_count = retry_count
        self.underlying_error = underlying_error


class ClientRegistrationError(HydraRouterError):
    """
    Exception raised for client registration and management issues.

    This exception is raised when there are problems with client registration,
    heartbeat management, or client lifecycle operations.
    """

    def __init__(
        self,
        message: str,
        client_id: Optional[str] = None,
        client_type: Optional[str] = None,
        operation: Optional[str] = None,
        registry_state: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize client registration error.

        Args:
            message: Human-readable error message
            client_id: ID of the client that caused the error
            client_type: Type of the client
            operation: The operation that failed (register, unregister, heartbeat, etc.)
            registry_state: Current state of the client registry
        """
        context = {}
        if client_id:
            context["client_id"] = client_id
        if client_type:
            context["client_type"] = client_type
        if operation:
            context["operation"] = operation
        if registry_state:
            context["registry_state"] = registry_state

        super().__init__(message, context)
        self.client_id = client_id
        self.client_type = client_type
        self.operation = operation
        self.registry_state = registry_state


class MessageRoutingError(HydraRouterError):
    """
    Exception raised for message routing failures.

    This exception is raised when messages cannot be routed properly
    between clients and servers.
    """

    def __init__(
        self,
        message: str,
        source_client: Optional[str] = None,
        target_client: Optional[str] = None,
        message_type: Optional[str] = None,
        routing_rule: Optional[str] = None,
        available_clients: Optional[list] = None,
    ):
        """
        Initialize message routing error.

        Args:
            message: Human-readable error message
            source_client: ID of the client that sent the message
            target_client: ID of the intended target client
            message_type: Type of message that failed to route
            routing_rule: The routing rule that was applied
            available_clients: List of currently available clients
        """
        context = {}
        if source_client:
            context["source_client"] = source_client
        if target_client:
            context["target_client"] = target_client
        if message_type:
            context["message_type"] = message_type
        if routing_rule:
            context["routing_rule"] = routing_rule
        if available_clients:
            context["available_clients"] = available_clients

        super().__init__(message, context)
        self.source_client = source_client
        self.target_client = target_client
        self.message_type = message_type
        self.routing_rule = routing_rule
        self.available_clients = available_clients


class TimeoutError(HydraRouterError):
    """
    Exception raised when operations exceed their timeout limits.

    This exception is raised for various timeout scenarios including
    message timeouts, connection timeouts, and operation timeouts.
    """

    def __init__(
        self,
        message: str,
        timeout_duration: Optional[float] = None,
        operation: Optional[str] = None,
        elapsed_time: Optional[float] = None,
    ):
        """
        Initialize timeout error.

        Args:
            message: Human-readable error message
            timeout_duration: The timeout duration that was exceeded
            operation: The operation that timed out
            elapsed_time: How long the operation actually took
        """
        context = {}
        if timeout_duration:
            context["timeout_duration"] = timeout_duration
        if operation:
            context["operation"] = operation
        if elapsed_time:
            context["elapsed_time"] = elapsed_time

        super().__init__(message, context)
        self.timeout_duration = timeout_duration
        self.operation = operation
        self.elapsed_time = elapsed_time


class ConfigurationError(HydraRouterError):
    """
    Exception raised for configuration-related issues.

    This exception is raised when there are problems with router
    configuration, invalid settings, or missing configuration values.
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        expected_type: Optional[str] = None,
        valid_values: Optional[list] = None,
    ):
        """
        Initialize configuration error.

        Args:
            message: Human-readable error message
            config_key: The configuration key that caused the error
            config_value: The invalid configuration value
            expected_type: Expected type for the configuration value
            valid_values: List of valid values for the configuration
        """
        context = {}
        if config_key:
            context["config_key"] = config_key
        if config_value is not None:
            context["config_value"] = config_value
        if expected_type:
            context["expected_type"] = expected_type
        if valid_values:
            context["valid_values"] = valid_values

        super().__init__(message, context)
        self.config_key = config_key
        self.config_value = config_value
        self.expected_type = expected_type
        self.valid_values = valid_values


class MessageFormatError(MessageValidationError):
    """
    Exception raised for message format conversion issues.

    This exception is a specialized form of MessageValidationError
    specifically for format conversion problems between ZMQMessage
    and RouterConstants formats.
    """

    def __init__(
        self,
        message: str,
        source_format: Optional[str] = None,
        target_format: Optional[str] = None,
        conversion_step: Optional[str] = None,
        original_message: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize message format error.

        Args:
            message: Human-readable error message
            source_format: The source message format
            target_format: The target message format
            conversion_step: The step in conversion that failed
            original_message: The original message before conversion
        """
        context = {}
        if source_format:
            context["source_format"] = source_format
        if target_format:
            context["target_format"] = target_format
        if conversion_step:
            context["conversion_step"] = conversion_step

        super().__init__(message, original_message, context=context)
        self.source_format = source_format
        self.target_format = target_format
        self.conversion_step = conversion_step


class ServerNotAvailableError(MessageRoutingError):
    """
    Exception raised when no server is available for client requests.

    This exception is raised when clients send messages that require
    server processing, but no server is currently connected to the router.
    """

    def __init__(
        self,
        message: str = "No server connected to handle client request",
        client_id: Optional[str] = None,
        message_type: Optional[str] = None,
        server_required: bool = True,
    ):
        """
        Initialize server not available error.

        Args:
            message: Human-readable error message
            client_id: ID of the client that made the request
            message_type: Type of message that requires server processing
            server_required: Whether a server is required for this operation
        """
        context = {"server_required": server_required, "available_servers": 0}

        super().__init__(
            message,
            source_client=client_id,
            message_type=message_type,
            routing_rule="client_to_server",
        )
        self.server_required = server_required


# Convenience functions for creating common exceptions
def create_validation_error(
    field_name: str,
    expected: str,
    actual: str,
    message: Optional[Dict[str, Any]] = None,
) -> MessageValidationError:
    """
    Create a message validation error for field validation failures.

    Args:
        field_name: Name of the field that failed validation
        expected: Expected value or type
        actual: Actual value or type found
        message: The message that failed validation

    Returns:
        MessageValidationError instance
    """
    error_msg = (
        f"Field '{field_name}' validation failed: expected {expected}, got {actual}"
    )
    return MessageValidationError(
        error_msg,
        invalid_message=message,
        field_name=field_name,
        expected_type=expected,
        actual_type=actual,
    )


def create_connection_error(
    address: str, port: int, underlying_error: Optional[Exception] = None
) -> ConnectionError:
    """
    Create a connection error for network connection failures.

    Args:
        address: Network address that failed
        port: Network port that failed
        underlying_error: The underlying exception

    Returns:
        ConnectionError instance
    """
    error_msg = f"Failed to connect to {address}:{port}"
    if underlying_error:
        error_msg += f" - {underlying_error}"

    return ConnectionError(
        error_msg, address=address, port=port, underlying_error=underlying_error
    )


def create_timeout_error(
    operation: str, timeout_duration: float, elapsed_time: Optional[float] = None
) -> TimeoutError:
    """
    Create a timeout error for operations that exceed time limits.

    Args:
        operation: The operation that timed out
        timeout_duration: The timeout duration that was exceeded
        elapsed_time: How long the operation actually took

    Returns:
        TimeoutError instance
    """
    error_msg = f"Operation '{operation}' timed out after {timeout_duration}s"
    if elapsed_time:
        error_msg += f" (elapsed: {elapsed_time}s)"

    return TimeoutError(
        error_msg,
        timeout_duration=timeout_duration,
        operation=operation,
        elapsed_time=elapsed_time,
    )
