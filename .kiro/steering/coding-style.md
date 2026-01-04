---
inclusion: always
---

# Coding Style Guidelines

This document outlines the coding style and patterns to follow for this project, based on the established patterns in the HydraRouter implementation.

## Constants Organization

### Structure
- All constants should be organized in dedicated files within the `constants/` directory
- Use descriptive class names prefixed with `D` (e.g., `DHydraServer`, `DGameConfig`)
- Group related constants into logical classes within the same file

### Example Structure
```python
# constants/DModuleName.py

class DModuleDefaults:
    """Default configuration values"""
    HOSTNAME: str = "localhost"
    PORT: int = 5757
    TIMEOUT: int = 30

class DModuleMessages:
    """User-facing messages with format placeholders"""
    CONNECTED: str = "Connected to {server_address}"
    ERROR: str = "Error occurred: {error_details}"
    CLEANUP: str = "Resources cleaned up successfully"

class DModuleConfig:
    """Configuration constants"""
    MAX_RETRIES: int = 3
    BUFFER_SIZE: int = 1024
```

### Usage Patterns
```python
# Import constants at module level
from project.constants.DModuleName import DModuleDefaults, DModuleMessages

class MyClass:
    def __init__(self, port=None):
        # Use constants for defaults
        self.port = port or DModuleDefaults.PORT

    def connect(self):
        # Use constants for messages with .format()
        print(DModuleMessages.CONNECTED.format(server_address=f"localhost:{self.port}"))
```

## Message Formatting

### String Templates
- All user-facing messages should use format string templates with named placeholders
- Use `.format()` method for string interpolation, not f-strings in constants
- Keep messages descriptive but concise

### Examples
```python
# ✅ Good - Named placeholders
CONNECTED: str = "HydraClient connected to {server_address}"
ERROR: str = "Operation failed: {error_type} - {details}"

# ❌ Avoid - f-strings in constants (won't work)
CONNECTED: str = f"HydraClient connected to {server_address}"

# ✅ Good - Usage
print(DMessages.CONNECTED.format(server_address="tcp://localhost:5757"))
```

## Class Design Patterns

### Constructor Parameters
- Use separate parameters instead of compound strings when possible
- Provide sensible defaults using constants
- Validate parameters when appropriate

### Example
```python
# ✅ Good - Separate parameters with defaults
def __init__(self, hostname=None, port=None):
    self.hostname = hostname or DDefaults.HOSTNAME
    self.port = port or DDefaults.PORT
    self.address = f"tcp://{self.hostname}:{self.port}"

# ❌ Less flexible - Single compound parameter
def __init__(self, server_address="tcp://localhost:5757"):
    self.server_address = server_address
```

### Error Handling
- Use constants for error messages
- Print descriptive error messages before exiting
- Include relevant context in error messages

```python
try:
    # operation
except Exception as e:
    print(DMessages.ERROR.format(operation="connection", details=str(e)))
    exit(1)
```

## File Organization

### Constants Directory Structure
```
constants/
├── __init__.py
├── DModuleName.py      # Module-specific constants
├── DGlobalConfig.py    # Project-wide configuration
└── DMessages.py        # Common message templates
```

### Import Conventions
```python
# Import specific constant classes, not entire modules
from project.constants.DModuleName import DModuleDefaults, DModuleMessages

# Use descriptive aliases if needed
from project.constants.DLongModuleName import DLongModuleDefaults as Defaults
```

## Benefits of This Approach

1. **Maintainability**: All configuration and messages centralized
2. **Consistency**: Uniform message formatting across the project
3. **Flexibility**: Easy to change defaults without touching implementation
4. **Testability**: Constants can be easily mocked or overridden for testing
5. **Internationalization**: Message templates ready for translation
6. **Documentation**: Constants serve as living documentation of configurable values

## Code Review Checklist

When reviewing code, ensure:
- [ ] Hard-coded strings are moved to constants
- [ ] Message formatting uses `.format()` with named placeholders
- [ ] Default values come from constants, not inline literals
- [ ] Constants are logically grouped in appropriate classes
- [ ] Import statements follow the established patterns
- [ ] Error messages include sufficient context for debugging

## Migration Guidelines

When refactoring existing code:
1. Identify hard-coded values and messages
2. Create appropriate constant classes
3. Replace literals with constant references
4. Update message formatting to use templates
5. Test that functionality remains unchanged
6. Update documentation if needed

This style promotes clean, maintainable, and professional code that scales well as the project grows.
