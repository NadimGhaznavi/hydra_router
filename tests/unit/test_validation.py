"""
Unit tests for message validation module.

Tests the MessageValidator class and its validation methods
for DRouter format messages.
"""

from hydra_router.constants.DRouter import DRouter
from hydra_router.validation import MessageValidator


class TestMessageValidator:
    """Test MessageValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = MessageValidator()

    def test_valid_message_passes_validation(self):
        """Test that a valid message passes validation."""
        valid_message = {
            DRouter.SENDER: DRouter.HYDRA_CLIENT,
            DRouter.ELEM: DRouter.SQUARE_REQUEST,
            DRouter.DATA: {"number": 5},
            DRouter.CLIENT_ID: "client-123",
            DRouter.TIMESTAMP: 1234567890.0,
            DRouter.REQUEST_ID: "req-456",
        }

        is_valid, error = self.validator.validate_router_message(valid_message)
        assert is_valid
        assert error == ""

    def test_minimal_valid_message_passes(self):
        """Test that a minimal valid message passes validation."""
        minimal_message = {
            DRouter.SENDER: DRouter.SIMPLE_CLIENT,
            DRouter.ELEM: DRouter.HEARTBEAT,
        }

        is_valid, error = self.validator.validate_router_message(minimal_message)
        assert is_valid
        assert error == ""

    def test_missing_sender_fails_validation(self):
        """Test that missing sender field fails validation."""
        invalid_message = {DRouter.ELEM: DRouter.SQUARE_REQUEST}

        is_valid, error = self.validator.validate_router_message(invalid_message)
        assert not is_valid
        assert DRouter.SENDER in error

    def test_missing_elem_fails_validation(self):
        """Test that missing elem field fails validation."""
        invalid_message = {DRouter.SENDER: DRouter.HYDRA_CLIENT}

        is_valid, error = self.validator.validate_router_message(invalid_message)
        assert not is_valid
        assert DRouter.ELEM in error

    def test_invalid_sender_type_fails_validation(self):
        """Test that invalid sender type fails validation."""
        invalid_message = {
            DRouter.SENDER: "InvalidSender",
            DRouter.ELEM: DRouter.SQUARE_REQUEST,
        }

        is_valid, error = self.validator.validate_router_message(invalid_message)
        assert not is_valid
        assert "sender" in error.lower()

    def test_non_dict_message_fails_validation(self):
        """Test that non-dictionary message fails validation."""
        invalid_messages = ["not a dict", 123, [], None]

        for invalid_message in invalid_messages:
            is_valid, error = self.validator.validate_router_message(invalid_message)
            assert not is_valid
            assert "dictionary" in error.lower()

    def test_field_type_validation(self):
        """Test field type validation."""
        # Test invalid sender type (not string)
        invalid_message = {
            DRouter.SENDER: 123,
            DRouter.ELEM: DRouter.HEARTBEAT,
        }
        is_valid, error = self.validator.validate_router_message(invalid_message)
        assert not is_valid
        assert "string" in error.lower()

        # Test invalid elem type (not string)
        invalid_message = {
            DRouter.SENDER: DRouter.HYDRA_CLIENT,
            DRouter.ELEM: 456,
        }
        is_valid, error = self.validator.validate_router_message(invalid_message)
        assert not is_valid
        assert "string" in error.lower()

        # Test invalid data type (not dict)
        invalid_message = {
            DRouter.SENDER: DRouter.HYDRA_CLIENT,
            DRouter.ELEM: DRouter.SQUARE_REQUEST,
            DRouter.DATA: "not a dict",
        }
        is_valid, error = self.validator.validate_router_message(invalid_message)
        assert not is_valid
        assert "dict" in error.lower()

        # Test invalid timestamp type (not number)
        invalid_message = {
            DRouter.SENDER: DRouter.HYDRA_CLIENT,
            DRouter.ELEM: DRouter.HEARTBEAT,
            DRouter.TIMESTAMP: "not a number",
        }
        is_valid, error = self.validator.validate_router_message(invalid_message)
        assert not is_valid
        assert "number" in error.lower()

    def test_validate_field_types_method(self):
        """Test the validate_field_types method directly."""
        valid_message = {
            DRouter.SENDER: DRouter.HYDRA_CLIENT,
            DRouter.ELEM: DRouter.SQUARE_REQUEST,
            DRouter.DATA: {"key": "value"},
            DRouter.CLIENT_ID: "client-123",
            DRouter.TIMESTAMP: 1234567890.0,
            DRouter.REQUEST_ID: "req-456",
        }

        is_valid, error = self.validator.validate_field_types(valid_message)
        assert is_valid
        assert error == ""

    def test_validate_sender_type_method(self):
        """Test the validate_sender_type method directly."""
        # Valid sender types
        for sender_type in DRouter.VALID_CLIENT_TYPES:
            assert self.validator.validate_sender_type(sender_type)

        # Invalid sender types
        invalid_senders = ["InvalidSender", "", None, 123]
        for sender in invalid_senders:
            assert not self.validator.validate_sender_type(sender)

    def test_get_validation_error_details(self):
        """Test the get_validation_error_details method."""
        invalid_message = {
            DRouter.SENDER: "InvalidSender",
            DRouter.ELEM: 123,
            DRouter.DATA: "not a dict",
        }

        error_details = self.validator.get_validation_error_details(invalid_message)
        assert isinstance(error_details, str)
        assert len(error_details) > 0
        assert "InvalidSender" in error_details

    def test_empty_message_fails_validation(self):
        """Test that empty message fails validation."""
        empty_message = {}

        is_valid, error = self.validator.validate_router_message(empty_message)
        assert not is_valid
        assert DRouter.SENDER in error

    def test_extra_fields_allowed(self):
        """Test that extra fields are allowed in messages."""
        message_with_extra_fields = {
            DRouter.SENDER: DRouter.HYDRA_CLIENT,
            DRouter.ELEM: DRouter.SQUARE_REQUEST,
            "extra_field": "extra_value",
            "another_field": 123,
        }

        is_valid, error = self.validator.validate_router_message(
            message_with_extra_fields
        )
        assert is_valid
        assert error == ""

    def test_all_client_types_valid(self):
        """Test that all defined client types are considered valid."""
        for client_type in DRouter.VALID_CLIENT_TYPES:
            message = {
                DRouter.SENDER: client_type,
                DRouter.ELEM: DRouter.HEARTBEAT,
            }

            is_valid, error = self.validator.validate_router_message(message)
            assert is_valid, f"Client type {client_type} should be valid"

    def test_router_as_sender_valid(self):
        """Test that HYDRA_ROUTER can be a valid sender."""
        message = {
            DRouter.SENDER: DRouter.HYDRA_ROUTER,
            DRouter.ELEM: DRouter.ERROR,
        }

        is_valid, error = self.validator.validate_router_message(message)
        assert is_valid
