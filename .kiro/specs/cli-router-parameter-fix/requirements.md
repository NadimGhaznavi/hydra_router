# Requirements Document

## Introduction

The Hydra Router CLI has a parameter mismatch issue where the CLI is attempting to pass `address` and `port` parameters to the HydraRouter constructor, but the constructor expects `router_address` and `router_port` parameters. This causes a TypeError when trying to start the router via the CLI.

## Glossary

- **CLI**: Command-Line Interface module (`hydra_router/cli.py`) that provides the `hydra-router` executable
- **HydraRouter**: The central router class (`hydra_router/router.py`) that manages client connections
- **Parameter_Mismatch**: The inconsistency between parameter names used in CLI and expected by HydraRouter constructor
- **Constructor_Signature**: The `__init__` method signature of the HydraRouter class
- **CLI_Arguments**: The parsed command-line arguments passed to the router initialization

## Requirements

### Requirement 1: CLI Parameter Consistency

**User Story:** As a user running the hydra-router CLI, I want the router to start successfully when I provide address and port parameters, so that I can deploy the router without encountering parameter mismatch errors.

#### Acceptance Criteria

1. WHEN the CLI passes address and port arguments to HydraRouter, THE HydraRouter constructor SHALL accept these parameters without errors
2. THE CLI parameter names SHALL match the HydraRouter constructor parameter names exactly
3. WHEN a user runs `hydra-router start --address 127.0.0.1 --port 5556`, THE router SHALL initialize successfully with the specified address and port
4. THE parameter mapping SHALL be consistent across all CLI commands that interact with HydraRouter
5. THE fix SHALL maintain backward compatibility with existing HydraRouter usage patterns

### Requirement 2: Error Prevention and Validation

**User Story:** As a developer using the HydraRouter programmatically, I want clear and consistent parameter names, so that I can avoid parameter mismatch errors in my code.

#### Acceptance Criteria

1. THE HydraRouter constructor parameter names SHALL be self-documenting and consistent with their usage
2. WHEN incorrect parameter names are used, THE system SHALL provide clear error messages indicating the expected parameter names
3. THE parameter validation SHALL occur at initialization time to catch errors early
4. THE documentation SHALL reflect the correct parameter names for both CLI and programmatic usage
5. THE type hints SHALL accurately reflect the expected parameter types and names

### Requirement 3: Consistent Interface Design

**User Story:** As a system administrator, I want consistent parameter naming across the entire Hydra Router system, so that I can easily understand and use different components without confusion.

#### Acceptance Criteria

1. THE parameter naming convention SHALL be consistent between CLI arguments and constructor parameters
2. THE CLI help text SHALL accurately reflect the parameter names used internally
3. THE configuration examples SHALL use the correct parameter names
4. THE error messages SHALL reference the correct parameter names when validation fails
5. THE system SHALL follow Python naming conventions for parameter names
