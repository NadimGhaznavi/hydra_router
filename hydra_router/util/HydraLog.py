"""
hydra_router/utils/HydraLog.py.

    Hydra Router
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2025-2006 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/hydra_router
    Website: https://hydra-router.readthedocs.io/en/latest/index.html
    License: GPL 3.0
"""

import logging

from hydra_router.constants.DHydraLog import LOG_LEVELS, DHydraLog


class HydraLog:
    """Hydra Router logging utility class."""

    def __init__(self, client_id: str, log_file=None, to_console=True):
        """Initialize the HydraLog instance.

        Args:
            client_id: Unique identifier for the logger
            log_file: Optional file path for log output
            to_console: Whether to output logs to console
        """
        self._logger = logging.getLogger(client_id)

        # The default logger log level
        self._logger.setLevel(LOG_LEVELS[DHydraLog.DEBUG])

        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Optional file handler
        if log_file:
            fh = logging.FileHandler(log_file)
            fh.setLevel(LOG_LEVELS[DHydraLog.DEBUG])
            fh.setFormatter(formatter)
            self._logger.addHandler(fh)

        # Optional console handler
        if to_console:
            ch = logging.StreamHandler()
            ch.setLevel(LOG_LEVELS[DHydraLog.DEBUG])
            ch.setFormatter(formatter)
            self._logger.addHandler(ch)

        self._logger.propagate = False

    def loglevel(self, loglevel):
        """Set the logging level.

        Args:
            loglevel: The log level to set
        """
        self._logger.setLevel(LOG_LEVELS[loglevel])

    def shutdown(self):
        """Shutdown the logger cleanly."""
        # Exit cleanly
        logging.shutdown()  # Flush all handler

    # Basic log message handling, wraps Python's logging object
    def info(self, message, extra=None):
        """Log an info message.

        Args:
            message: The message to log
            extra: Optional extra data for the log record
        """
        self._logger.info(message, extra=extra)

    def debug(self, message, extra=None):
        """Log a debug message.

        Args:
            message: The message to log
            extra: Optional extra data for the log record
        """
        self._logger.debug(message, extra=extra)

    def warning(self, message, extra=None):
        """Log a warning message.

        Args:
            message: The message to log
            extra: Optional extra data for the log record
        """
        self._logger.warning(message, extra=extra)

    def error(self, message, extra=None):
        """Log an error message.

        Args:
            message: The message to log
            extra: Optional extra data for the log record
        """
        self._logger.error(message, extra=extra)

    def critical(self, message, extra=None):
        """Log a critical message.

        Args:
            message: The message to log
            extra: Optional extra data for the log record
        """
        self._logger.critical(message, extra=extra)
