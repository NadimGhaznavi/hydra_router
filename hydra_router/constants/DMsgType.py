"""
Message type definitions for the Hydra Router system.

This module defines the MsgType enumeration used throughout the system
for consistent message type identification and routing.
"""

from enum import Enum


class MsgType(Enum):
    """Enumeration of message types for internal application use."""

    HEARTBEAT = "heartbeat"
    SQUARE_REQUEST = "square_request"
    SQUARE_RESPONSE = "square_response"
    ERROR = "error"
    CLIENT_REGISTRY_REQUEST = "client_registry_request"
    CLIENT_REGISTRY_RESPONSE = "client_registry_response"
    START_SIMULATION = "start_simulation"
    STOP_SIMULATION = "stop_simulation"
    PAUSE_SIMULATION = "pause_simulation"
    RESUME_SIMULATION = "resume_simulation"
    RESET_SIMULATION = "reset_simulation"
    GET_SIMULATION_STATUS = "get_simulation_status"
    STATUS_UPDATE = "status_update"
    SIMULATION_STARTED = "simulation_started"
    SIMULATION_STOPPED = "simulation_stopped"
    SIMULATION_PAUSED = "simulation_paused"
    SIMULATION_RESUMED = "simulation_resumed"
    SIMULATION_RESET = "simulation_reset"
