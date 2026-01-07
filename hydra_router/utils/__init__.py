# hydra_router/utils/__init__.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

"""
Utility components for Hydra Router.
"""

try:
    from .HydraLog import HydraLog
    from .HydraMsg import HydraMsg

    __all__ = ["HydraLog", "HydraMsg"]
except ImportError:
    # Handle import errors during documentation builds
    __all__ = []
