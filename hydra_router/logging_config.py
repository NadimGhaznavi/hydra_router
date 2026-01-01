"""
Logging configuration for Hydra Router.

This module provides centralized logging configuration for all components
of the Hydra Router system.
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Any, Dict, Optional, cast


def get_logging_config(  # type: ignore[misc]
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_console: bool = True,
    enable_file: bool = True,
) -> Dict[str, Any]:
    """
    Get logging configuration dictionary.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (default: logs/hydra_router.log)
        enable_console: Whether to enable console logging
        enable_file: Whether to enable file logging

    Returns:
        Logging configuration dictionary
    """
    if log_file is None:
        log_file = Path("logs") / "hydra_router.log"

    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "%(levelname)s - %(name)s - %(message)s",
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}',
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {},
        "loggers": {
            "hydra_router": {
                "level": log_level,
                "handlers": [],
                "propagate": False,
            },
            "hydra_router.router": {
                "level": log_level,
                "handlers": [],
                "propagate": True,
            },
            "hydra_router.mq_client": {
                "level": log_level,
                "handlers": [],
                "propagate": True,
            },
            "hydra_router.simple_client": {
                "level": log_level,
                "handlers": [],
                "propagate": True,
            },
            "hydra_router.simple_server": {
                "level": log_level,
                "handlers": [],
                "propagate": True,
            },
        },
        "root": {
            "level": "WARNING",
            "handlers": [],
        },
    }

    # Add console handler if enabled
    if enable_console:
        config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        }
        config["loggers"]["hydra_router"]["handlers"].append("console")  # type: ignore
        config["root"]["handlers"].append("console")  # type: ignore

    # Add file handler if enabled
    if enable_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "detailed",
            "filename": str(log_file),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8",
        }
        config["loggers"]["hydra_router"]["handlers"].append("file")  # type: ignore
        config["root"]["handlers"].append("file")  # type: ignore

    return config


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_console: bool = True,
    enable_file: bool = True,
) -> None:
    """
    Set up logging for the Hydra Router application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (default: logs/hydra_router.log)
        enable_console: Whether to enable console logging
        enable_file: Whether to enable file logging
    """
    config = get_logging_config(
        log_level=log_level,
        log_file=log_file,
        enable_console=enable_console,
        enable_file=enable_file,
    )

    logging.config.dictConfig(config)

    # Log startup message
    logger = logging.getLogger("hydra_router")
    logger.info(f"Logging initialized - Level: {log_level}")
    if enable_file and log_file:
        logger.info(f"Log file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f"hydra_router.{name}")


# Convenience function for quick setup
def configure_logging_from_args(
    verbose: int = 0,
    quiet: bool = False,
    log_file: Optional[str] = None,
) -> None:
    """
    Configure logging based on command-line arguments.

    Args:
        verbose: Verbosity level (0=INFO, 1=DEBUG, 2+=DEBUG with more detail)
        quiet: If True, disable console logging
        log_file: Path to log file
    """
    # Determine log level from verbosity
    if verbose == 0:
        log_level = "INFO"
    elif verbose == 1:
        log_level = "DEBUG"
    else:
        log_level = "DEBUG"
        # Enable more verbose logging for third-party libraries
        logging.getLogger("zmq").setLevel(logging.DEBUG)

    # Convert log_file string to Path if provided
    log_file_path = Path(log_file) if log_file else None

    setup_logging(
        log_level=log_level,
        log_file=log_file_path,
        enable_console=not quiet,
        enable_file=True,
    )


# Example usage and testing
if __name__ == "__main__":
    # Test logging configuration
    setup_logging(log_level="DEBUG")

    logger = get_logger("test")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
