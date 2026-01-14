---
inclusion: always
---

# Coding Style Guidelines

This document outlines the coding style and patterns to follow for this project, based on the established patterns in the HydraRouter implementation.

## Code Formatting Standards

### Line Length
- **CRITICAL**: Maximum line length is **88 characters**
- This applies to all code, comments, and docstrings
- Use line breaks and proper indentation for long lines
- Tools like `black` will enforce this automatically

### Examples
```python
# ✅ Good - Under 88 characters
def short_function(param1: str, param2: int) -> bool:
    return True

# ✅ Good - Properly wrapped long line
def long_function_name(
    parameter_one: str,
    parameter_two: int,
    parameter_three: Optional[str] = None
) -> Dict[str, Any]:
    return {"result": "success"}

# ❌ Bad - Over 88 characters
def bad_function(param1: str, param2: int, param3: str, param4: bool) -> Dict[str, Any]:
    return {"this_line_is_way_too_long_and_violates_the_88_character_limit": True}
```

## Constants Organization

### Core Principle: Three Categories of Constants

All constants fall into three distinct categories, each serving a different purpose:

#### 1. Default Values (Configuration)
Numeric values, timeouts, sizes, and other configurable parameters that control behavior.

```python
class DHydraServerDef:
    """Default configuration values"""
    HOSTNAME: str = "localhost"
    PORT: int = 5757
    TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    BUFFER_SIZE: int = 1024
    HEARTBEAT_INTERVAL: float = 5.0
```

**Purpose**: Provide sensible defaults that can be overridden by users.

#### 2. Human-Readable Labels (Messages)
Strings intended for human consumption - log messages, error messages, help text, UI labels.

```python
class DHydraServerMsg:
    """User-facing messages with format placeholders"""
    CONNECTED: str = "Connected to {server_address}"
    ERROR: str = "HydraServer error: {e}"
    CLEANUP: str = "Resources cleaned up successfully"
    STARTING: str = "Starting server on {address}:{port}"
    STOP_HELP: str = "Press Ctrl+C to stop the server"
```

**Purpose**: Consistent messaging, easy internationalization, centralized wording.

#### 3. Computer-Readable Labels (Protocol Values)
Strings used in protocols, APIs, serialization - method names, identifiers, field names.

```python
class DModule:
    """Module/component identifiers for routing"""
    HYDRA_ROUTER: str = "hydra-router"
    HYDRA_CLIENT: str = "hydra-client"
    HYDRA_SERVER: str = "hydra-server"
    GAME_SERVICE: str = "game-service"

class DMethod:
    """RPC method names"""
    PING: str = "ping"
    PONG: str = "pong"
    HEARTBEAT: str = "heartbeat"
    REGISTER: str = "register"

class DHydraMsg:
    """Message field names for JSON serialization"""
    ID: str = "id"
    SENDER: str = "sender"
    TARGET: str = "target"
    METHOD: str = "method"
    PAYLOAD: str = "payload"
    V: str = "version"
```

**Purpose**: Protocol consistency, eliminate magic strings, enable safe refactoring.

### Naming Convention

Use suffixes to indicate category:
- `*Def` or `*Defaults` - Default values (configuration)
- `*Msg` or `*Messages` - Human-readable labels (messages)
- No suffix - Computer-readable labels (protocol values)

### Complete Example

```python
# constants/DHydra.py

# Computer-readable: Protocol identifiers
class DModule:
    HYDRA_ROUTER: str = "hydra-router"
    HYDRA_CLIENT: str = "hydra-client"

# Computer-readable: RPC methods
class DMethod:
    PING: str = "ping"
    PONG: str = "pong"

# Default values: Configuration
class DHydraServerDef:
    HOSTNAME: str = "localhost"
    PORT: int = 5757
    TIMEOUT: int = 30

# Human-readable: User messages
class DHydraServerMsg:
    STARTING: str = "Starting server on {address}:{port}"
    ERROR: str = "HydraServer error: {e}"
    BIND: str = "Server bound to {bind_address}"
```

### Usage Patterns

```python
from hydra_router.constants.DHydra import (
    DModule,           # Computer-readable
    DMethod,           # Computer-readable
    DHydraServerDef,   # Default values
    DHydraServerMsg,   # Human-readable
)

class HydraServer:
    def __init__(self, port=None):
        # Use default values for configuration
        self.port = port or DHydraServerDef.PORT
        
        # Use computer-readable labels for protocol
        self.identity = DModule.HYDRA_SERVER
        
    def start(self):
        # Use human-readable labels for logging
        self.log.info(
            DHydraServerMsg.STARTING.format(
                address=self.address,
                port=self.port
            )
        )
        
    def handle_message(self, msg):
        # Use computer-readable labels for dispatch
        if msg.method == DMethod.PING:
            return self.ping(msg)
```

### Why This Matters

**Default Values** can change without breaking protocols:
```python
# Safe to change: PORT: int = 5757 → PORT: int = 8080
# Only affects default behavior, not wire protocol
```

**Human-Readable Labels** can be reworded or translated:
```python
# Safe to change: "Starting server" → "Server initializing"
# Only affects user-facing text, not functionality
```

**Computer-Readable Labels** define the protocol contract:
```python
# Breaking change: PING: str = "ping" → PING: str = "health_check"
# Changes wire protocol, requires version bump
```

This categorization makes it clear which constants are part of the API contract versus implementation details.

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

## Eliminating Magic Strings

### The Problem with Magic Strings
Magic strings are hard-coded string literals scattered throughout code that represent important values like method names, identifiers, or configuration keys. They create maintenance nightmares:

```python
# ❌ Bad - Magic strings everywhere
msg = HydraMsg(sender="client-123", target="hydra-router", method="ping")
if msg.method == "ping":
    return self.handle_ping()
elif msg.method == "pong":
    return self.handle_pong()

# What if you typo "ping" as "pign" somewhere? Silent failure!
# What if you need to rename "ping" to "health_check"? Find/replace nightmare!
```

### The Constants Solution
By defining all string literals as constants, you get:
- **Type safety**: Typos become NameErrors caught immediately
- **Refactoring safety**: Change once in constants, works everywhere
- **IDE support**: Autocomplete and go-to-definition
- **Self-documentation**: Constant names explain purpose

```python
# ✅ Good - Constants eliminate magic strings
from hydra_router.constants.DHydra import DModule, DMethod

msg = HydraMsg(
    sender=DModule.CLIENT,
    target=DModule.HYDRA_ROUTER,
    method=DMethod.PING
)

if msg.method == DMethod.PING:
    return self.handle_ping()
elif msg.method == DMethod.PONG:
    return self.handle_pong()

# Typo "DMethod.PIGN" → NameError caught immediately!
# Rename DMethod.PING → change once, works everywhere
```

### Real-World Example from HydraRouter

```python
# constants/DHydra.py
class DModule:
    """Module/component identifiers"""
    HYDRA_ROUTER: str = "hydra-router"
    HYDRA_CLIENT: str = "hydra-client"
    HYDRA_SERVER: str = "hydra-server"
    GAME_SERVICE: str = "game-service"

class DMethod:
    """RPC method names"""
    PING: str = "ping"
    PONG: str = "pong"
    HEARTBEAT: str = "heartbeat"
    REGISTER: str = "register"

class DHydraMsg:
    """Message field names for serialization"""
    ID: str = "id"
    SENDER: str = "sender"
    TARGET: str = "target"
    METHOD: str = "method"
    PAYLOAD: str = "payload"
    V: str = "version"
```

### Usage in Code

```python
# Message creation - no magic strings
msg = HydraMsg(
    sender=DModule.HYDRA_CLIENT,
    target=DModule.HYDRA_ROUTER,
    method=DMethod.PING,
    payload={}
)

# Serialization - field names from constants
def to_dict(self) -> Dict[str, Any]:
    return {
        DHydraMsg.ID: self._id,
        DHydraMsg.SENDER: self._sender,
        DHydraMsg.TARGET: self._target,
        DHydraMsg.METHOD: self._method,
        DHydraMsg.PAYLOAD: self._payload,
        DHydraMsg.V: DHydra.PROTOCOL_VERSION,
    }

# Method dispatch - method names from constants
async def dispatch(self, msg: HydraMsg) -> HydraMsg:
    if msg.method == DMethod.PING:
        return await self.ping(msg)
    elif msg.method == DMethod.HEARTBEAT:
        return await self.heartbeat(msg)
```

### Benefits

1. **Catch errors early**: Typos become NameErrors at import time
2. **Safe refactoring**: Change constant value once, all uses update
3. **Protocol versioning**: Easy to see all protocol strings in one place
4. **IDE support**: Autocomplete shows all available methods/modules
5. **Grep-friendly**: Find all uses of a method with simple search
6. **Type hints**: Can use Literal types for validation

### Rule: No String Literals for Protocol Values

**Never use string literals for:**
- Module/component identifiers
- RPC method names
- Message field names
- Protocol versions
- Status codes
- Error types

**Always define them as constants first.**

## Benefits of This Approach

1. **Maintainability**: All configuration and messages centralized
2. **Consistency**: Uniform message formatting across the project
3. **Flexibility**: Easy to change defaults without touching implementation
4. **Testability**: Constants can be easily mocked or overridden for testing
5. **Internationalization**: Message templates ready for translation
6. **Documentation**: Constants serve as living documentation of configurable values
7. **No Magic Strings**: Protocol values defined once, used safely everywhere

## Code Review Checklist

When reviewing code, ensure:
- [ ] **Line length does not exceed 88 characters**
- [ ] **No magic strings** - all protocol values use constants
- [ ] Hard-coded strings are moved to constants
- [ ] Message formatting uses `.format()` with named placeholders
- [ ] Default values come from constants, not inline literals
- [ ] Constants are logically grouped in appropriate classes
- [ ] Import statements follow the established patterns
- [ ] Error messages include sufficient context for debugging
- [ ] Code passes `flake8` linting with 88-character limit
- [ ] Code is formatted with `black` using 88-character line length

## Migration Guidelines

When refactoring existing code:
1. Identify hard-coded values and messages
2. Create appropriate constant classes
3. Replace literals with constant references
4. Update message formatting to use templates
5. Test that functionality remains unchanged
6. Update documentation if needed

This style promotes clean, maintainable, and professional code that scales well as the project grows.
