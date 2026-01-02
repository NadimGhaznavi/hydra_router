"""
Message validation framework for the Hydra Router system.

This module provides comprehensive message validation with detailed error reporting
for RouterConstants format messages and other validation needs.
"""

from typing import Any, Dict, Tuple

from .router_constants import RouterConstants


class MessageValidator:
    """
    Comprehensive message validator for RouterConstants format messages.

    Provides detailed validation with specific error reporting to help
    identify and resolve message format issues.
    """

    def __init__(self) -> None:
        """Initialize the message validator."""
        self.router_constants = RouterConstants

    def validate_router_message(self, message: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a message against RouterConstants format requirements.

        Args:
            message: The message dictionary to validate

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if message is valid, False otherwise
            - error_message: Empty string if valid, detailed error if invalid
        """
        # 1. Type validation
        if not isinstance(message, dict):
            return False, f"Message must be dictionary, got {type(message).__name__}"

        # 2. Required field validation
        missing_fields = []
        for field in self.router_constants.REQUIRED_FIELDS:
            if field not in message:
                missing_fields.append(field)

        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"

        # 3. Field type and value validation
        sender_valid, sender_error = self._validate_sender_field(message)
        if not sender_valid:
            return False, sender_error

        elem_valid, elem_error = self._validate_elem_field(message)
        if not elem_valid:
            return False, elem_error

        # 4. Optional field validation
        optional_valid, optional_error = self._validate_optional_fields(message)
        if not optional_valid:
            return False, optional_error

        # 5. Message size validation
        size_valid, size_error = self._validate_message_size(message)
        if not size_valid:
            return False, size_error

        return True, ""

    def _validate_sender_field(self, message: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate the sender field."""
        sender = message.get(self.router_constants.SENDER)

        if not isinstance(sender, str):
            return False, f"Field 'sender' must be string, got {type(sender).__name__}"

        if not sender.strip():
            return (
                False,
                f"Field 'sender' must be non-empty string, got: {repr(sender)}",
            )

        if not self.router_constants.is_valid_client_type(sender):
            valid_types = ", ".join(self.router_constants.VALID_CLIENT_TYPES)
            return (
                False,
                f"Invalid sender type '{sender}', expected one of: {valid_types}",
            )

        return True, ""

    def _validate_elem_field(self, message: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate the elem field."""
        elem = message.get(self.router_constants.ELEM)

        if not isinstance(elem, str):
            return False, f"Field 'elem' must be string, got {type(elem).__name__}"

        if not elem.strip():
            return False, f"Field 'elem' must be non-empty string, got: {repr(elem)}"

        return True, ""

    def _validate_optional_fields(self, message: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate optional fields if present."""
        # Validate data field
        if self.router_constants.DATA in message:
            data = message[self.router_constants.DATA]
            if data is not None and not isinstance(data, dict):
                return (
                    False,
                    f"Field 'data' must be dict or None, got {type(data).__name__}",
                )

        # Validate client_id field
        if self.router_constants.CLIENT_ID in message:
            client_id = message[self.router_constants.CLIENT_ID]
            if not isinstance(client_id, str):
                return (
                    False,
                    f"Field 'client_id' must be string, got {type(client_id).__name__}",
                )
            if not client_id.strip():
                return (
                    False,
                    f"Field 'client_id' must be non-empty string, got: {repr(client_id)}",
                )

        # Validate timestamp field
        if self.router_constants.TIMESTAMP in message:
            timestamp = message[self.router_constants.TIMESTAMP]
            if not isinstance(timestamp, (int, float)):
                return (
                    False,
                    f"Field 'timestamp' must be number, got {type(timestamp).__name__}",
                )
            if timestamp < 0:
                return (
                    False,
                    f"Field 'timestamp' must be non-negative, got: {timestamp}",
                )

        # Validate request_id field
        if self.router_constants.REQUEST_ID in message:
            request_id = message[self.router_constants.REQUEST_ID]
            if not isinstance(request_id, str):
                return (
                    False,
                    f"Field 'request_id' must be string, got {type(request_id).__name__}",
                )
            if not request_id.strip():
                return (
                    False,
                    f"Field 'request_id' must be non-empty string, got: {repr(request_id)}",
                )

        return True, ""

    def _validate_message_size(self, message: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate message size constraints."""
        try:
            import json

            message_size = len(json.dumps(message).encode("utf-8"))

            if message_size > self.router_constants.MAX_MESSAGE_SIZE:
                return (
                    False,
                    f"Message size {message_size} bytes exceeds maximum {self.router_constants.MAX_MESSAGE_SIZE} bytes",
                )

            # Validate data field size if present
            if (
                self.router_constants.DATA in message
                and message[self.router_constants.DATA] is not None
            ):
                data_size = len(
                    json.dumps(message[self.router_constants.DATA]).encode("utf-8")
                )
                if data_size > self.router_constants.MAX_DATA_SIZE:
                    return (
                        False,
                        f"Data field size {data_size} bytes exceeds maximum {self.router_constants.MAX_DATA_SIZE} bytes",
                    )

        except (TypeError, ValueError) as e:
            return False, f"Message serialization failed: {e}"

        return True, ""

    def validate_field_types(self, message: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate field types without checking required fields.

        Useful for partial message validation during construction.

        Args:
            message: The message dictionary to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(message, dict):
            return False, f"Message must be dictionary, got {type(message).__name__}"

        for field_name, field_value in message.items():
            if field_name == self.router_constants.SENDER:
                if not isinstance(field_value, str):
                    return (
                        False,
                        f"Field 'sender' must be string, got {type(field_value).__name__}",
                    )
            elif field_name == self.router_constants.ELEM:
                if not isinstance(field_value, str):
                    return (
                        False,
                        f"Field 'elem' must be string, got {type(field_value).__name__}",
                    )
            elif field_name == self.router_constants.DATA:
                if field_value is not None and not isinstance(field_value, dict):
                    return (
                        False,
                        f"Field 'data' must be dict or None, got {type(field_value).__name__}",
                    )
            elif field_name == self.router_constants.CLIENT_ID:
                if not isinstance(field_value, str):
                    return (
                        False,
                        f"Field 'client_id' must be string, got {type(field_value).__name__}",
                    )
            elif field_name == self.router_constants.TIMESTAMP:
                if not isinstance(field_value, (int, float)):
                    return (
                        False,
                        f"Field 'timestamp' must be number, got {type(field_value).__name__}",
                    )
            elif field_name == self.router_constants.REQUEST_ID:
                if not isinstance(field_value, str):
                    return (
                        False,
                        f"Field 'request_id' must be string, got {type(field_value).__name__}",
                    )

        return True, ""

    def validate_sender_type(self, sender: str) -> bool:
        """
        Validate if a sender type is valid.

        Args:
            sender: The sender type to validate

        Returns:
            True if valid, False otherwise
        """
        return self.router_constants.is_valid_client_type(sender)

    def get_validation_error_details(self, message: Dict[str, Any]) -> str:
        """
        Get detailed validation error information for troubleshooting.

        Args:
            message: The message that failed validation

        Returns:
            Detailed error information string
        """
        details = []

        # Basic message info
        details.append("=== Message Validation Error Details ===")
        details.append(f"Message type: {type(message).__name__}")

        if isinstance(message, dict):
            details.append(f"Present fields: {list(message.keys())}")
            field_types = {k: type(v).__name__ for k, v in message.items()}
            details.append(f"Field types: {field_types}")

        # Expected format
        details.append("\n=== Expected RouterConstants Format ===")
        expected_format = {
            self.router_constants.SENDER: f"string (one of: {', '.join(self.router_constants.VALID_CLIENT_TYPES)})",
            self.router_constants.ELEM: "string (message type)",
            self.router_constants.DATA: "dict (optional)",
            self.router_constants.CLIENT_ID: "string (optional)",
            self.router_constants.TIMESTAMP: "number (optional)",
            self.router_constants.REQUEST_ID: "string (optional)",
        }
        for field, description in expected_format.items():
            required = field in self.router_constants.REQUIRED_FIELDS
            status = "REQUIRED" if required else "OPTIONAL"
            details.append(f"  {field}: {description} [{status}]")

        # Validation results
        details.append("\n=== Validation Results ===")
        is_valid, error = self.validate_router_message(message)
        details.append(f"Valid: {is_valid}")
        if not is_valid:
            details.append(f"Error: {error}")

        # Debugging hints
        details.append("\n=== Debugging Hints ===")
        if isinstance(message, dict):
            # Check for common issues
            if "message_type" in message and self.router_constants.ELEM not in message:
                details.append(
                    "- Detected 'message_type' field instead of 'elem' - this suggests ZMQMessage format instead of RouterConstants format"
                )

            missing_required = [
                f for f in self.router_constants.REQUIRED_FIELDS if f not in message
            ]
            if missing_required:
                details.append(f"- Missing required fields: {missing_required}")

            invalid_fields = [
                f for f in message.keys() if f not in self.router_constants.ALL_FIELDS
            ]
            if invalid_fields:
                details.append(
                    f"- Unknown fields (not in RouterConstants format): {invalid_fields}"
                )

        details.append("- Ensure MQClient format conversion is working correctly")
        details.append(
            "- Check that client is using RouterConstants format for router communication"
        )

        return "\n".join(details)

    def create_valid_message_template(self, sender: str, elem: str) -> Dict[str, Any]:
        """
        Create a valid message template with required fields.

        Args:
            sender: The sender type (must be valid client type)
            elem: The message element/type

        Returns:
            Valid message template dictionary

        Raises:
            ValueError: If sender type is invalid
        """
        if not self.validate_sender_type(sender):
            valid_types = ", ".join(self.router_constants.VALID_CLIENT_TYPES)
            raise ValueError(
                f"Invalid sender type '{sender}', must be one of: {valid_types}"
            )

        return {
            self.router_constants.SENDER: sender,
            self.router_constants.ELEM: elem,
            self.router_constants.DATA: None,
            self.router_constants.CLIENT_ID: "",
            self.router_constants.TIMESTAMP: 0.0,
            self.router_constants.REQUEST_ID: "",
        }


# Convenience functions for common validation tasks
def validate_message(message: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Convenience function to validate a RouterConstants format message.

    Args:
        message: The message to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    validator = MessageValidator()
    return validator.validate_router_message(message)


def is_valid_client_type(client_type: str) -> bool:
    """
    Convenience function to check if a client type is valid.

    Args:
        client_type: The client type to check

    Returns:
        True if valid, False otherwise
    """
    return RouterConstants.is_valid_client_type(client_type)


def get_validation_details(message: Dict[str, Any]) -> str:
    """
    Convenience function to get detailed validation error information.

    Args:
        message: The message that failed validation

    Returns:
        Detailed error information string
    """
    validator = MessageValidator()
    return validator.get_validation_error_details(message)
