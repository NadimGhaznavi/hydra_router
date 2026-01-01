"""
Hydra Router - A ZeroMQ-based message routing system.

This package provides a standalone message router that enables reliable communication
between multiple clients and a single server through a centralized routing pattern.
"""

__version__ = "0.2.2"
__author__ = "Nadim-Daniel Ghaznavi"
__email__ = "nghaznavi@gmail.com"

from .logging_config import get_logger, setup_logging
from .mq_client import MQClient
from .router import HydraRouter
from .router_constants import RouterConstants

__all__ = [
    "RouterConstants",
    "MQClient",
    "HydraRouter",
    "setup_logging",
    "get_logger",
]
