"""
Hydra Router - A ZeroMQ-based message routing system.

This package provides a standalone message router that enables reliable communication
between multiple clients and a single server through a centralized routing pattern.
"""

__version__ = "0.3.9"
__author__ = "Nadim-Daniel Ghaznavi"
__email__ = "nghaznavi@gmail.com"

from .constants.DRouter import DRouter
from .mq_client import MQClient
from .router import HydraRouter
from .util.HydraLog import HydraLog

__all__ = [
    "DRouter",
    "MQClient",
    "HydraRouter",
    "HydraLog",
]
