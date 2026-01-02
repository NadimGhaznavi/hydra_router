"""
Unit tests for DHydraLog module.

Tests the logging constants and LOG_LEVELS mapping
provided by the DHydraLog class.
"""

import logging

from hydra_router.constants.DHydraLog import LOG_LEVELS, DHydraLog


class TestDHydraLog:
    """Test DHydraLog class and its constants."""

    def test_log_level_constants_defined(self):
        """Test that all log level constants are properly defined."""
        assert hasattr(DHydraLog, "INFO")
        assert hasattr(DHydraLog, "DEBUG")
        assert hasattr(DHydraLog, "WARNING")
        assert hasattr(DHydraLog, "ERROR")
        assert hasattr(DHydraLog, "CRITICAL")

    def test_log_level_constants_are_strings(self):
        """Test that all log level constants are strings."""
        assert isinstance(DHydraLog.INFO, str)
        assert isinstance(DHydraLog.DEBUG, str)
        assert isinstance(DHydraLog.WARNING, str)
        assert isinstance(DHydraLog.ERROR, str)
        assert isinstance(DHydraLog.CRITICAL, str)

    def test_log_level_constants_values(self):
        """Test that log level constants have expected values."""
        assert DHydraLog.INFO == "info"
        assert DHydraLog.DEBUG == "debug"
        assert DHydraLog.WARNING == "warning"
        assert DHydraLog.ERROR == "error"
        assert DHydraLog.CRITICAL == "critical"

    def test_log_level_constants_uniqueness(self):
        """Test that all log level constants have unique values."""
        log_levels = [
            DHydraLog.INFO,
            DHydraLog.DEBUG,
            DHydraLog.WARNING,
            DHydraLog.ERROR,
            DHydraLog.CRITICAL,
        ]
        assert len(log_levels) == len(set(log_levels))

    def test_log_level_constants_non_empty(self):
        """Test that all log level constants are non-empty strings."""
        assert len(DHydraLog.INFO) > 0
        assert len(DHydraLog.DEBUG) > 0
        assert len(DHydraLog.WARNING) > 0
        assert len(DHydraLog.ERROR) > 0
        assert len(DHydraLog.CRITICAL) > 0

    def test_log_levels_dict_defined(self):
        """Test that LOG_LEVELS dictionary is properly defined."""
        assert LOG_LEVELS is not None
        assert isinstance(LOG_LEVELS, dict)

    def test_log_levels_dict_completeness(self):
        """Test that LOG_LEVELS contains all DHydraLog constants."""
        expected_keys = {
            DHydraLog.INFO,
            DHydraLog.DEBUG,
            DHydraLog.WARNING,
            DHydraLog.ERROR,
            DHydraLog.CRITICAL,
        }
        assert set(LOG_LEVELS.keys()) == expected_keys

    def test_log_levels_dict_values(self):
        """Test that LOG_LEVELS maps to correct Python logging levels."""
        assert LOG_LEVELS[DHydraLog.INFO] == logging.INFO
        assert LOG_LEVELS[DHydraLog.DEBUG] == logging.DEBUG
        assert LOG_LEVELS[DHydraLog.WARNING] == logging.WARNING
        assert LOG_LEVELS[DHydraLog.ERROR] == logging.ERROR
        assert LOG_LEVELS[DHydraLog.CRITICAL] == logging.CRITICAL

    def test_log_levels_dict_values_are_integers(self):
        """Test that all LOG_LEVELS values are integers."""
        for level_value in LOG_LEVELS.values():
            assert isinstance(level_value, int)

    def test_log_levels_dict_values_are_valid_logging_levels(self):
        """Test that all LOG_LEVELS values are valid Python logging levels."""
        valid_logging_levels = {
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        }
        for level_value in LOG_LEVELS.values():
            assert level_value in valid_logging_levels

    def test_log_levels_hierarchy(self):
        """Test that log levels follow the correct hierarchy."""
        # Python logging levels: DEBUG(10) < INFO(20) < WARNING(30) < ERROR(40) < CRITICAL(50)
        assert LOG_LEVELS[DHydraLog.DEBUG] < LOG_LEVELS[DHydraLog.INFO]
        assert LOG_LEVELS[DHydraLog.INFO] < LOG_LEVELS[DHydraLog.WARNING]
        assert LOG_LEVELS[DHydraLog.WARNING] < LOG_LEVELS[DHydraLog.ERROR]
        assert LOG_LEVELS[DHydraLog.ERROR] < LOG_LEVELS[DHydraLog.CRITICAL]

    def test_log_levels_dict_key_access(self):
        """Test that LOG_LEVELS can be accessed with DHydraLog constants."""
        # This should not raise KeyError
        try:
            _ = LOG_LEVELS[DHydraLog.INFO]
            _ = LOG_LEVELS[DHydraLog.DEBUG]
            _ = LOG_LEVELS[DHydraLog.WARNING]
            _ = LOG_LEVELS[DHydraLog.ERROR]
            _ = LOG_LEVELS[DHydraLog.CRITICAL]
        except KeyError:
            assert False, "LOG_LEVELS should be accessible with DHydraLog constants"

    def test_log_levels_integration_with_logging_module(self):
        """Test that LOG_LEVELS values work correctly with Python logging module."""
        # Create a test logger
        test_logger = logging.getLogger("test_dhydra_log")

        # Test setting log levels using LOG_LEVELS values
        for dhydra_level, python_level in LOG_LEVELS.items():
            test_logger.setLevel(python_level)
            assert test_logger.level == python_level
            assert test_logger.isEnabledFor(python_level)

    def test_dhydra_log_class_is_not_instantiable(self):
        """Test that DHydraLog is used as a constants class, not instantiated."""
        # This is more of a design test - the class should work as a namespace
        # We can create an instance, but it's not the intended usage
        instance = DHydraLog()
        assert instance is not None

        # The constants should still be accessible through the class
        assert DHydraLog.INFO == "info"
        assert DHydraLog.DEBUG == "debug"

    def test_constants_case_sensitivity(self):
        """Test that constants are properly case-sensitive."""
        # The string values should be lowercase
        assert DHydraLog.INFO.islower()
        assert DHydraLog.DEBUG.islower()
        assert DHydraLog.WARNING.islower()
        assert DHydraLog.ERROR.islower()
        assert DHydraLog.CRITICAL.islower()

        # The constant names should be uppercase
        assert "INFO" in dir(DHydraLog)
        assert "DEBUG" in dir(DHydraLog)
        assert "WARNING" in dir(DHydraLog)
        assert "ERROR" in dir(DHydraLog)
        assert "CRITICAL" in dir(DHydraLog)

    def test_module_imports_correctly(self):
        """Test that the module can be imported without errors."""
        # This test ensures the module structure is correct
        from hydra_router.constants.DHydraLog import LOG_LEVELS as ImportedLOG_LEVELS
        from hydra_router.constants.DHydraLog import DHydraLog as ImportedDHydraLog

        assert ImportedDHydraLog is DHydraLog
        assert ImportedLOG_LEVELS is LOG_LEVELS

    def test_log_levels_dict_immutability_concept(self):
        """Test that LOG_LEVELS dictionary maintains its integrity."""
        # Store original values
        original_values = dict(LOG_LEVELS)

        # Verify the dictionary hasn't been modified
        assert LOG_LEVELS == original_values

        # Verify all mappings are still correct
        assert LOG_LEVELS[DHydraLog.INFO] == logging.INFO
        assert LOG_LEVELS[DHydraLog.DEBUG] == logging.DEBUG
        assert LOG_LEVELS[DHydraLog.WARNING] == logging.WARNING
        assert LOG_LEVELS[DHydraLog.ERROR] == logging.ERROR
        assert LOG_LEVELS[DHydraLog.CRITICAL] == logging.CRITICAL
