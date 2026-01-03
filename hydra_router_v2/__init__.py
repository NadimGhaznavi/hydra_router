"""
Hydra Router v2 - Clean implementation based on requirements.

A ZeroMQ-based message routing system that provides reliable communication
between multiple clients and a single server through a centralized routing pattern.
"""

__version__ = "2.0.0"
__author__ = "Hydra Router Team"

from .constants import DRouter
from .zmq_message import ZMQMessage

# TODO: Import additional modules as they are implemented
# from .mq_client import MQClient
# from .hydra_router import HydraRouter
# from .simple_client import SimpleClient
# from .simple_server import SimpleServer

__all__ = [
    "DRouter",
    "ZMQMessage",
    # TODO: Add additional exports as modules are implemented
    # "MQClient",
    # "HydraRouter",
    # "SimpleClient",
    # "SimpleServer",
]
