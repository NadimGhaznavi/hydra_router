# hydra_router/client/__init__.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

"""
Client components for Hydra Router.
"""

try:
    from .HydraClient import HydraClient
    from .HydraClientPing import HydraClientPing

    __all__ = ["HydraClient", "HydraClientPing"]
except ImportError:
    # Handle import errors during documentation builds
    __all__ = []
