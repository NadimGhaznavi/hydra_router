"""
DRouter - Message format definitions and constants for the Hydra Router system.

This module provides centralized constants and message format definitions for all
components of the Hydra Router system, ensuring consistent communication between
clients, servers, and the router.
"""

from typing import Any, Dict, Optional


class DRouter:
    """
    Centralized constants and message format definitions for the Hydra Router system.

    This class provides:
    - Client/Server type definitions
    - Message structure field names
    - System message types
    - Network configuration constants
    - Validation rules and limits
    """

    # Message Format Fields (RouterConstants format)
    SENDER = "sender"
    ELEM = "elem"
    DATA = "data"
    CLIENT_ID = "client_id"
    TIMESTAMP = "timestamp"
    REQUEST_ID = "request_id"

    # Required fields for RouterConstants format
    REQUIRED_FIELDS = [SENDER, ELEM, TIMESTAMP]

    # All valid fields for RouterConstants format
    ALL_FIELDS = [SENDER, ELEM, DATA, CLIENT_ID, TIMESTAMP, REQUEST_ID]

    # Client/Server Types
    HYDRA_CLIENT = "HydraClient"
    HYDRA_SERVER = "HydraServer"
    SIMPLE_CLIENT = "SimpleClient"
    SIMPLE_SERVER = "SimpleServer"
    HYDRA_ROUTER = "HydraRouter"

    # Valid client types that can connect
    VALID_CLIENT_TYPES = [HYDRA_CLIENT, HYDRA_SERVER, SIMPLE_CLIENT, SIMPLE_SERVER]

    # Message Types (elem values)
    HEARTBEAT = "heartbeat"
    SQUARE_REQUEST = "square_request"
    SQUARE_RESPONSE = "square_response"
    CLIENT_REGISTRY_REQUEST = "client_registry_request"
    CLIENT_REGISTRY_RESPONSE = "client_registry_response"
    ERROR = "error"
    NO_SERVER_CONNECTED = "no_server_connected"

    # System Configuration
    DEFAULT_ROUTER_ADDRESS = "localhost"
    DEFAULT_ROUTER_PORT = 5556
    DEFAULT_HEARTBEAT_INTERVAL = 5.0  # seconds
    DEFAULT_CLIENT_TIMEOUT = 30.0  # seconds
    DEFAULT_MESSAGE_TIMEOUT = 10.0  # seconds
    MAX_CLIENTS = 10
    MAX_MESSAGE_SIZE = 1024 * 1024  # 1MB
    MAX_DATA_SIZE = 512 * 1024  # 512KB

    @classmethod
    def create_message(
        cls,
        sender: str,
        elem: str,
        timestamp: float,
        data: Optional[Dict[str, Any]] = None,
        client_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a RouterConstants format message.

        Args:
            sender: Client type sending the message
            elem: Message type/element
            timestamp: Message timestamp
            data: Optional message data payload
            client_id: Optional client identifier
            request_id: Optional request correlation ID

        Returns:
            RouterConstants format message dictionary
        """
        message = {
            cls.SENDER: sender,
            cls.ELEM: elem,
            cls.TIMESTAMP: timestamp,
        }

        if data is not None:
            message[cls.DATA] = data
        if client_id is not None:
            message[cls.CLIENT_ID] = client_id
        if request_id is not None:
            message[cls.REQUEST_ID] = request_id

        return message

    @classmethod
    def validate_message_format(cls, message: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate a message against RouterConstants format.

        Args:
            message: Message to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(message, dict):
            return False, f"Message must be dictionary, got {type(message).__name__}"

        # Check required fields
        missing_fields = [
            field for field in cls.REQUIRED_FIELDS if field not in message
        ]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"

        # Validate sender type
        sender = message.get(cls.SENDER)
        if not isinstance(sender, str) or not sender:
            return (
                False,
                f"Field 'sender' must be non-empty string, got: {repr(sender)}",
            )

        if sender not in cls.VALID_CLIENT_TYPES and sender != cls.HYDRA_ROUTER:
            valid_types = ", ".join(cls.VALID_CLIENT_TYPES + [cls.HYDRA_ROUTER])
            return (
                False,
                f"Invalid sender type '{sender}', expected one of: {valid_types}",
            )

        # Validate elem field
        elem = message.get(cls.ELEM)
        if not isinstance(elem, str) or not elem:
            return False, f"Field 'elem' must be non-empty string, got: {repr(elem)}"

        # Validate optional fields if present
        data = message.get(cls.DATA)
        if data is not None and not isinstance(data, dict):
            return (
                False,
                f"Field 'data' must be dict or None, got {type(data).__name__}",
            )

        client_id = message.get(cls.CLIENT_ID)
        if client_id is not None and (not isinstance(client_id, str) or not client_id):
            return (
                False,
                f"Field 'client_id' must be non-empty string, got: {repr(client_id)}",
            )

        timestamp = message.get(cls.TIMESTAMP)
        if not isinstance(timestamp, (int, float)):
            return (
                False,
                f"Field 'timestamp' must be number, got {type(timestamp).__name__}",
            )

        request_id = message.get(cls.REQUEST_ID)
        if request_id is not None and (
            not isinstance(request_id, str) or not request_id
        ):
            return (
                False,
                f"Field 'request_id' must be non-empty string, got: {repr(request_id)}",
            )

        return True, ""
