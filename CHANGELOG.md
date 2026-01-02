# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [Release 0.2.5] - 2026-01-01 20:07


### Added
- **MQ Client**: Complete ZeroMQ client library implementation with comprehensive async communication capabilities
  - Full MQClient class with automatic message format conversion between ZMQMessage and RouterConstants
  - Connection lifecycle management with heartbeat functionality and background task handling
  - Request/response pattern with timeout handling and correlation IDs for reliable communication
  - Message handler registration system for event-driven processing and custom message handling
  - Client registry querying and connection status management for network topology awareness
  - Support for both client and server application types with comprehensive validation
  - MessageType enum and ZMQMessage dataclass for type-safe internal message handling

## [Release 0.2.4] - 2026-01-01 19:43


### Added
- **Router Constants**: Comprehensive RouterConstants module with message format definitions, client/server types, and validation helpers
  - Complete client/server type definitions (HydraClient, HydraServer, SimpleClient, SimpleServer)
  - Message structure field names and validation constants
  - System, simulation, and error message type definitions
  - Configuration constants for timeouts, ports, and message size limits
  - Utility methods for client type validation and message categorization
  - Support for simple client/server square calculation workflow
  - Client registry query message types
- **Message Validation**: Complete message validation framework with detailed error reporting and type checking
  - MessageValidator class with comprehensive RouterConstants format validation
  - Field type validation with specific error messages
  - Message size constraint validation
  - Detailed debugging information for troubleshooting format issues
  - Convenience functions for common validation tasks
  - Message template creation for valid RouterConstants format
- **Exception Handling**: Comprehensive exception hierarchy for router-specific errors with context information
  - HydraRouterError base class with context support
  - MessageValidationError for format validation failures
  - ConnectionError for network communication issues
  - ClientRegistrationError for client management problems
  - MessageRoutingError for routing failures
  - TimeoutError for operation timeout scenarios
  - ConfigurationError for config-related issues
  - MessageFormatError for format conversion problems
  - ServerNotAvailableError for missing server scenarios
  - Convenience functions for common exception creation

## [Release 0.2.3] - 2026-01-01 17:57


### Changed
- **CI**: Updated GitHub Actions upload-artifact action from v3 to v4 for improved compatibility

### Fixed
- **Logging**: Added type safety checks for handler list operations to prevent AttributeError exceptions

## [Release 0.2.2] - 2026-01-01 17:45


### Changed
- **Logging**: Fixed code formatting and removed unused import for better code quality

## [Release 0.2.1] - 2026-01-01 17:37


### Changed
- **Scripts**: Enhanced version update script to include test file version synchronization

## [Release 0.2.0] - 2026-01-01 17:33


### Added
- **Development Environment**: Complete development environment setup with pre-commit hooks, CI/CD pipeline, and logging system
- **Logging System**: Comprehensive logging configuration with file rotation, console output, and configurable levels
- **CI/CD Pipeline**: GitHub Actions workflow with multi-Python testing, security scanning, and package building
- **Pre-commit Hooks**: Code quality enforcement with Black, isort, flake8, mypy, and bandit security checks
- **Test Coverage**: Comprehensive test suite for logging configuration with 95% coverage

### Changed
- **Scripts**: Updated project references from AI Hydra to Hydra Router in version update script
- **Specs**: Marked Task 1.1 and Task 1.2 acceptance criteria as completed in implementation tasks
- **CI**: Added comprehensive GitHub Actions test workflow with multi-Python version testing, linting, type checking, and security scanning
- **Code Quality**: Fixed all type annotations, docstrings, and import sorting across the codebase

### Fixed
- **Pre-commit**: Simplified bandit configuration for cleaner output and better compatibility
