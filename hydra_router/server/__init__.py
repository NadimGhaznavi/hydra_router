# hydra_router/server/__init__.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

"""
Server components for Hydra Router.
"""

try:
    from .HydraServer import HydraServer
    from .HydraServerPong import HydraServerPong

    __all__ = ["HydraServer", "HydraServerPong"]
except ImportError:
    # Handle import errors during documentation builds
    __all__ = []
