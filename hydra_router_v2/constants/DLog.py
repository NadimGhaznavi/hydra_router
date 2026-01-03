"""
DLog - Logging configuration constants for the Hydra Router system.

This module provides centralized logging configuration and level definitions
for consistent logging across all components.
"""

import logging


class DLog:
    """
    Centralized logging configuration constants.

    Provides logging levels, formats, and configuration for the Hydra Router system.
    """

    # Logging levels
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    # Logging format
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Date format
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    # Log level mapping to Python logging levels
    LEVELS = {
        DEBUG: logging.DEBUG,
        INFO: logging.INFO,
        WARNING: logging.WARNING,
        ERROR: logging.ERROR,
        CRITICAL: logging.CRITICAL,
    }

    @classmethod
    def get_level(cls, level_name: str) -> int:
        """
        Get Python logging level from string name.

        Args:
            level_name: String name of logging level

        Returns:
            Python logging level integer
        """
        return cls.LEVELS.get(level_name.upper(), logging.INFO)

    @classmethod
    def create_formatter(cls) -> logging.Formatter:
        """
        Create a standard logging formatter.

        Returns:
            Configured logging formatter
        """
        return logging.Formatter(cls.FORMAT, cls.DATE_FORMAT)
