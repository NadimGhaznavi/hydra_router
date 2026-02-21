# hydra_router/constants/DHydra.py
#
#    Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

import logging
from enum import StrEnum
from typing import Final, Mapping


# Project globals
class DHydra:
    """
    Global project constants and version information.

    Contains the current version string and other project-wide constants
    used throughout the HydraRouter package.
    """

    HEARTBEAT_INTERVAL: Final[float] = 5.0
    NETWORK_TIMEOUT: Final[float] = 2.0
    PROTOCOL_VERSION: Final[int] = 1
    RANDOM_SEED: Final[int] = 1970
    VERSION: Final[str] = "0.16.0"


# HydraMsg class constants
class DHydraMsg(StrEnum):
    """
    Attribute definitions for HydraMsg class messages.
    """

    METHOD = "method"
    SENDER = "sender"
    TARGET = "target"
    PAYLOAD = "payload"
    PROTOCOL_VERSION = "protocol_version"


# HydraClient messages
class DHydraClientMsg:
    """
    Message templates for HydraClient logging and user feedback.

    Contains formatted string templates with placeholders for dynamic
    values. Use .format() method to substitute actual values.
    """

    CLEANUP: Final[str] = "HydraClient cleanup complete"
    CONNECTED: Final[str] = "HydraClient connected to {server_address}"
    ERROR: Final[str] = "HydraClient error: {e}"
    LOGLEVEL_HELP: Final[str] = "Log level: DEBUG, INFO, WARNING, ERROR or CRITICAL"
    PORT_HELP: Final[str] = "Server port to connect to (default: {server_port})"
    RECEIVED: Final[str] = "Received response: {response}"
    SENDING: Final[str] = "Sending request: {message}"
    SERVER_HELP: Final[
        str
    ] = "Server hostname to connect to (default: {server_address})"


# HydraLog levels
class DHydraLog(StrEnum):
    """
    Logging level constants for HydraLog configuration.

    Defines string constants for different logging levels that map
    to Python's standard logging levels via the LOG_LEVELS dictionary.
    """

    INFO = "info"
    DEBUG = "debug"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# HydraLog defaults
class DHydraLogDef:
    """
    Hydra Log defaults.
    """

    DEFAULT_LOG_LEVEL: Final[DHydraLog] = DHydraLog.DEBUG


# HydraRouter defaults
class DHydraRouterDef:
    """
    Hydra Router defaults.
    """

    HOSTNAME: Final[str] = "localhost"
    PORT: Final[int] = 5757
    HEARTBEAT_PORT: Final[int] = 5758


# HydraServer defaults
class DHydraServerDef:
    """
    Hydra Server defaults.
    """

    HOSTNAME: Final[str] = "localhost"
    PORT: Final[int] = 5759


# HydraServer messages
class DHydraServerMsg:
    """
    Message templates for HydraServer logging and user feedback.

    Contains formatted string templates with placeholders for dynamic
    values. Use .format() method to substitute actual values.
    """

    ADDRESS_HELP: Final[str] = "Address to bind to (default: '*' for all interfaces)"
    BIND: Final[str] = "HydraServer bound to {bind_address}"
    CLEANUP: Final[str] = "HydraServer cleanup complete"
    ERROR: Final[str] = "HydraServer error: {e}"
    LOGLEVEL_HELP: Final[str] = "Log level: DEBUG, INFO, WARNING, ERROR or CRITICAL"
    LOOP_UP: Final[
        str
    ] = "HydraServer message loop on {address}:{port} is up and running"
    PORT_HELP: Final[str] = "Port to bind to (default: {port})"
    RECEIVE: Final[str] = "Received request: {message}"
    SENT: Final[str] = "Sent response: {response}"
    SHUTDOWN: Final[str] = "HydraServer shutting down..."
    STARTING: Final[str] = "Starting HydraServer on {address}:{port}"
    STOP_HELP: Final[str] = "Press Ctrl+C to stop the server"
    USER_STOP: Final[str] = "Server stopped by user"


# Hydra ZeroMQ RPC Methods
class DMethod(StrEnum):
    HEARTBEAT = "heartbeat"
    HEARTBEAT_REPLY = "heartbeat_reply"
    PING = "ping"
    PING_ROUTER = "ping_router"
    PING_SERVER = "ping_server"
    PONG = "pong"
    START = "start"
    STOP = "stop"


# Hydra Router Modules
class DModule(StrEnum):
    """
    Module identifier constants for HydraRouter components.

    Provides standardized string identifiers for different HydraRouter
    modules, used in logging and component identification.
    """

    HYDRA_CLIENT = "HydraClient"
    HYDRA_MQ = "HydraMQ"
    HYDRA_ROUTER = "HydraRouter"
    HYDRA_SERVER = "HydraServer"


# HydraLog levels dictionary
# Mapping of HydraLog level strings to Python logging level integers.
# Used by HydraLog to convert string-based log level configuration
# to the integer values expected by Python's logging module.
LOG_LEVELS: Mapping[DHydraLog, int] = {
    DHydraLog.INFO: logging.INFO,
    DHydraLog.DEBUG: logging.DEBUG,
    DHydraLog.WARNING: logging.WARNING,
    DHydraLog.ERROR: logging.ERROR,
    DHydraLog.CRITICAL: logging.CRITICAL,
}
