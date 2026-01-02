"""
constants/DHydraLog.py.

    Hydra Router
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/hydra_router
    Website: https://hydra-router.readthedocs.io/en/latest/index.html
    License: GPL 3.0
"""

import logging


class DHydraLog:
    """Logging Constants."""

    INFO: str = "info"
    DEBUG: str = "debug"
    WARNING: str = "warning"
    ERROR: str = "error"
    CRITICAL: str = "critical"


LOG_LEVELS: dict = {
    DHydraLog.INFO: logging.INFO,
    DHydraLog.DEBUG: logging.DEBUG,
    DHydraLog.WARNING: logging.WARNING,
    DHydraLog.ERROR: logging.ERROR,
    DHydraLog.CRITICAL: logging.CRITICAL,
}
