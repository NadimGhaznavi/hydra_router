# hydra_router/utils/HydraLog.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

import logging

from hydra_router.constants.DHydra import DHydraLog, LOG_LEVELS


class HydraLog:
    def __init__(self, client_id: str, log_file=None, to_console=True):
        self._logger = logging.getLogger(client_id)

        # The default logger log level
        self._logger.setLevel(LOG_LEVELS[DHydraLog.DEFAULT])

        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Optional file handler
        if log_file:
            fh = logging.FileHandler(log_file)
            fh.setLevel(LOG_LEVELS[DHydraLog.DEFAULT])
            fh.setFormatter(formatter)
            self._logger.addHandler(fh)

        # Optional console handler
        if to_console:
            ch = logging.StreamHandler()
            ch.setLevel(LOG_LEVELS[DHydraLog.DEFAULT])
            ch.setFormatter(formatter)
            self._logger.addHandler(ch)

        self._logger.propagate = False

    def loglevel(self, loglevel):
        self._logger.setLevel(LOG_LEVELS[loglevel])

    def shutdown(self):
        # Exit cleanly
        logging.shutdown()  # Flush all handler

    # Basic log message handling, wraps Python's logging object
    def info(self, message, extra=None):
        self._logger.info(message, extra=extra)

    def debug(self, message, extra=None):
        self._logger.debug(message, extra=extra)

    def warning(self, message, extra=None):
        self._logger.warning(message, extra=extra)

    def error(self, message, extra=None):
        self._logger.error(message, extra=extra)

    def critical(self, message, extra=None):
        self._logger.critical(message, extra=extra)
