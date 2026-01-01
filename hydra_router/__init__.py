"""
Hydra Router - A ZeroMQ-based message routing system.

This package provides a standalone message router that enables reliable communication
between multiple clients and a single server through a centralized routing pattern.
"""

__version__ = "0.1.0"
__author__ = "Nadim-Daniel Ghaznavi"
__email__ = "nghaznavi@gmail.com"

from .router_constants import RouterConstants
from .mq_client import MQClient
from .router import HydraRouter

__all__ = [
    "RouterConstants",
    "MQClient",
    "HydraRouter",
]
