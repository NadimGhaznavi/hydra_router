"""
DMsgType - Message type definitions for the Hydra Router system.

This module defines the DMsgType enumeration used throughout the system
for consistent message type identification and routing.
"""

from enum import Enum


class DMsgType(Enum):
    """Enumeration of message types for internal application use."""

    HEARTBEAT = "heartbeat"
    SQUARE_REQUEST = "square_request"
    SQUARE_RESPONSE = "square_response"
    CLIENT_REGISTRY_REQUEST = "client_registry_request"
    CLIENT_REGISTRY_RESPONSE = "client_registry_response"
    ERROR = "error"
    NO_SERVER_CONNECTED = "no_server_connected"
