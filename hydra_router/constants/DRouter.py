"""
DRouter - Message format definitions and constants for the Hydra Router system.

This module provides centralized constants and message format definitions for all
components of the Hydra Router system, ensuring consistent communication between
clients, servers, and the router.
"""


class DRouter:
    """
    Centralized constants and message format definitions for the Hydra Router system.

    This class provides:
    - Client/Server type definitions
    - Message structure field names
    - System message types
    - Simple client/server message types
    - Client registry message types
    - Simulation control commands
    - Network configuration constants
    """

    # Client/Server Types
    HYDRA_CLIENT = "HydraClient"
    HYDRA_SERVER = "HydraServer"
    HYDRA_ROUTER = "HydraRouter"
    SIMPLE_CLIENT = "SimpleClient"
    SIMPLE_SERVER = "SimpleServer"

    # Valid Client Types (for validation)
    VALID_CLIENT_TYPES = [
        HYDRA_CLIENT,
        HYDRA_SERVER,
        HYDRA_ROUTER,
        SIMPLE_CLIENT,
        SIMPLE_SERVER,
    ]

    # Message Structure Keys
    SENDER = "sender"
    ELEM = "elem"
    DATA = "data"
    CLIENT_ID = "client_id"
    TIMESTAMP = "timestamp"
    REQUEST_ID = "request_id"

    # System Messages
    HEARTBEAT = "heartbeat"
    STATUS = "status"
    ERROR = "error"

    # Simple Client/Server Messages
    SQUARE_REQUEST = "square_request"
    SQUARE_RESPONSE = "square_response"

    # Client Registry Messages
    CLIENT_REGISTRY_REQUEST = "client_registry_request"
    CLIENT_REGISTRY_RESPONSE = "client_registry_response"

    # Simulation Control Commands
    START_SIMULATION = "start_simulation"
    STOP_SIMULATION = "stop_simulation"
    PAUSE_SIMULATION = "pause_simulation"
    RESUME_SIMULATION = "resume_simulation"
    RESET_SIMULATION = "reset_simulation"
    GET_SIMULATION_STATUS = "get_simulation_status"

    # Status Update Messages
    STATUS_UPDATE = "status_update"
    SIMULATION_STARTED = "simulation_started"
    SIMULATION_STOPPED = "simulation_stopped"
    SIMULATION_PAUSED = "simulation_paused"
    SIMULATION_RESUMED = "simulation_resumed"
    SIMULATION_RESET = "simulation_reset"

    # Error Messages
    NO_SERVER_CONNECTED = "no_server_connected"
    INVALID_MESSAGE_FORMAT = "invalid_message_format"
    UNKNOWN_CLIENT_TYPE = "unknown_client_type"
    CONNECTION_FAILED = "connection_failed"
    TIMEOUT_ERROR = "timeout_error"

    # Configuration Constants
    HEARTBEAT_INTERVAL = 5  # seconds
    DEFAULT_ROUTER_PORT = 5556
    DEFAULT_ROUTER_ADDRESS = "0.0.0.0"
    DEFAULT_CLIENT_TIMEOUT = 30  # seconds
    DEFAULT_MESSAGE_TIMEOUT = 10  # seconds

    # Message Format Validation Constants
    REQUIRED_FIELDS = [SENDER, ELEM]
    OPTIONAL_FIELDS = [DATA, CLIENT_ID, TIMESTAMP, REQUEST_ID]
    ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS

    # Maximum message sizes (in bytes)
    MAX_MESSAGE_SIZE = 1024 * 1024  # 1MB
    MAX_DATA_SIZE = 512 * 1024  # 512KB

    @classmethod
    def is_valid_client_type(cls, client_type: str) -> bool:
        """
        Check if a client type is valid.

        Args:
            client_type: The client type to validate

        Returns:
            True if the client type is valid, False otherwise
        """
        return client_type in cls.VALID_CLIENT_TYPES

    @classmethod
    def get_all_message_types(cls) -> list[str]:
        """
        Get all defined message types.

        Returns:
            List of all message type constants
        """
        message_types = [
            # System messages
            cls.HEARTBEAT,
            cls.STATUS,
            cls.ERROR,
            # Simple client/server messages
            cls.SQUARE_REQUEST,
            cls.SQUARE_RESPONSE,
            # Client registry messages
            cls.CLIENT_REGISTRY_REQUEST,
            cls.CLIENT_REGISTRY_RESPONSE,
            # Simulation control commands
            cls.START_SIMULATION,
            cls.STOP_SIMULATION,
            cls.PAUSE_SIMULATION,
            cls.RESUME_SIMULATION,
            cls.RESET_SIMULATION,
            cls.GET_SIMULATION_STATUS,
            # Status updates
            cls.STATUS_UPDATE,
            cls.SIMULATION_STARTED,
            cls.SIMULATION_STOPPED,
            cls.SIMULATION_PAUSED,
            cls.SIMULATION_RESUMED,
            cls.SIMULATION_RESET,
            # Error messages
            cls.NO_SERVER_CONNECTED,
            cls.INVALID_MESSAGE_FORMAT,
            cls.UNKNOWN_CLIENT_TYPE,
            cls.CONNECTION_FAILED,
            cls.TIMEOUT_ERROR,
        ]
        return message_types

    @classmethod
    def is_system_message(cls, message_type: str) -> bool:
        """
        Check if a message type is a system message.

        Args:
            message_type: The message type to check

        Returns:
            True if it's a system message, False otherwise
        """
        system_messages = [cls.HEARTBEAT, cls.STATUS, cls.ERROR]
        return message_type in system_messages

    @classmethod
    def is_simulation_command(cls, message_type: str) -> bool:
        """
        Check if a message type is a simulation control command.

        Args:
            message_type: The message type to check

        Returns:
            True if it's a simulation command, False otherwise
        """
        simulation_commands = [
            cls.START_SIMULATION,
            cls.STOP_SIMULATION,
            cls.PAUSE_SIMULATION,
            cls.RESUME_SIMULATION,
            cls.RESET_SIMULATION,
            cls.GET_SIMULATION_STATUS,
        ]
        return message_type in simulation_commands

    @classmethod
    def get_required_fields(cls) -> list[str]:
        """
        Get the list of required message fields.

        Returns:
            List of required field names
        """
        return cls.REQUIRED_FIELDS.copy()

    @classmethod
    def get_optional_fields(cls) -> list[str]:
        """
        Get the list of optional message fields.

        Returns:
            List of optional field names
        """
        return cls.OPTIONAL_FIELDS.copy()

    @classmethod
    def get_all_fields(cls) -> list[str]:
        """
        Get the list of all valid message fields.

        Returns:
            List of all valid field names
        """
        return cls.ALL_FIELDS.copy()


# Convenience constants for backward compatibility and ease of use
HEARTBEAT_INTERVAL = DRouter.HEARTBEAT_INTERVAL
DEFAULT_ROUTER_PORT = DRouter.DEFAULT_ROUTER_PORT
DEFAULT_ROUTER_ADDRESS = DRouter.DEFAULT_ROUTER_ADDRESS
