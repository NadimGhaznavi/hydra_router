"""
Test logging configuration.
"""

import logging
import tempfile
from pathlib import Path

import pytest

from hydra_router.logging_config import (
    configure_logging_from_args,
    get_logger,
    get_logging_config,
    setup_logging,
)


class TestLoggingConfig:
    """Test logging configuration functionality."""

    def test_get_logging_config_default(self):
        """Test default logging configuration."""
        config = get_logging_config()

        assert config["version"] == 1
        assert "hydra_router" in config["loggers"]
        assert config["loggers"]["hydra_router"]["level"] == "INFO"
        assert "console" in config["handlers"]
        assert "file" in config["handlers"]

    def test_get_logging_config_custom_level(self):
        """Test logging configuration with custom level."""
        config = get_logging_config(log_level="DEBUG")

        assert config["loggers"]["hydra_router"]["level"] == "DEBUG"
        assert config["handlers"]["console"]["level"] == "DEBUG"
        assert config["handlers"]["file"]["level"] == "DEBUG"

    def test_get_logging_config_console_only(self):
        """Test logging configuration with console only."""
        config = get_logging_config(enable_file=False)

        assert "console" in config["handlers"]
        assert "file" not in config["handlers"]
        assert "console" in config["loggers"]["hydra_router"]["handlers"]
        assert "file" not in config["loggers"]["hydra_router"]["handlers"]

    def test_get_logging_config_file_only(self):
        """Test logging configuration with file only."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            config = get_logging_config(log_file=log_file, enable_console=False)

            assert "file" in config["handlers"]
            assert "console" not in config["handlers"]
            assert "file" in config["loggers"]["hydra_router"]["handlers"]
            assert "console" not in config["loggers"]["hydra_router"]["handlers"]

    def test_setup_logging(self):
        """Test logging setup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_logging(log_level="DEBUG", log_file=log_file)

            # Test that logger is configured
            logger = logging.getLogger("hydra_router")
            assert logger.level == logging.DEBUG

            # Test that log file is created
            logger.info("Test message")
            assert log_file.exists()

    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test_module")

        assert logger.name == "hydra_router.test_module"
        assert isinstance(logger, logging.Logger)

    def test_configure_logging_from_args_default(self):
        """Test configuring logging from default arguments."""
        configure_logging_from_args()

        logger = logging.getLogger("hydra_router")
        assert logger.level == logging.INFO

    def test_configure_logging_from_args_verbose(self):
        """Test configuring logging with verbose flag."""
        configure_logging_from_args(verbose=1)

        logger = logging.getLogger("hydra_router")
        assert logger.level == logging.DEBUG

    def test_configure_logging_from_args_quiet(self):
        """Test configuring logging with quiet flag."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = str(Path(temp_dir) / "test.log")
            configure_logging_from_args(quiet=True, log_file=log_file)

            # Should still create log file even when quiet
            logger = logging.getLogger("hydra_router")
            logger.info("Test message")
            assert Path(log_file).exists()

    def test_logging_hierarchy(self):
        """Test that logging hierarchy works correctly."""
        setup_logging(log_level="DEBUG")

        # Test different loggers in the hierarchy
        main_logger = logging.getLogger("hydra_router")
        router_logger = logging.getLogger("hydra_router.router")
        client_logger = logging.getLogger("hydra_router.mq_client")

        assert main_logger.level == logging.DEBUG
        # Child loggers should propagate to parent
        assert router_logger.propagate is True
        assert client_logger.propagate is True
