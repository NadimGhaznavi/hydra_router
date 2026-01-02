# Design Document

## Overview

This design addresses the failing `test_basic_usage_example` test by updating the `examples/basic_usage.py` script to actually demonstrate MQClient creation and usage instead of showing placeholder messages. The test expects specific output text that indicates real functionality rather than "Coming in Task X.Y" messages.

## Architecture

The solution involves modifying the existing `examples/basic_usage.py` script to:

1. Actually create an MQClient instance
2. Print the expected "Creating MQClient" message
3. Demonstrate basic usage patterns
4. Maintain the existing "Basic Usage Example" header that the test also checks for

## Components and Interfaces

### Modified Components

**examples/basic_usage.py**
- Update the main() function to create an actual MQClient instance
- Add proper logging/printing of the MQClient creation
- Remove placeholder messages and replace with real functionality
- Maintain async structure for proper MQClient usage

### Interface Requirements

**Output Interface**
- Must include "Basic Usage Example" text (already present)
- Must include "Creating MQClient" text (needs to be added)
- Should demonstrate actual MQClient instantiation
- Must return exit code 0 (no errors)

## Data Models

No new data models are required. The script will use existing:
- `HydraRouter` class from hydra_router module
- `MQClient` class from hydra_router module
- Standard Python asyncio patterns

## Implementation Approach

### Script Structure
```python
async def main() -> None:
    # Print header (already exists)
    print("Hydra Router Basic Usage Example")
    print("================================")

    # Demonstrate MQClient creation (new)
    print("Creating MQClient")
    client = MQClient(
        router_address="tcp://localhost:5556",
        client_type="demo-client",
        client_id="basic-usage-demo"
    )

    # Show that creation was successful
    print(f"✓ MQClient created: {client}")
    print(f"✓ HydraRouter class: {HydraRouter}")
    print("✓ Basic usage demonstration complete")
```

### Key Changes
1. Replace placeholder messages with actual MQClient instantiation
2. Add "Creating MQClient" print statement before creating the client
3. Create a real MQClient instance with appropriate parameters
4. Show successful creation with confirmation message

## Error Handling

The script should handle potential errors gracefully:
- Import errors (should not occur as imports already work)
- MQClient creation errors (use try/catch if needed)
- Maintain exit code 0 for successful execution

## Testing Strategy

### Unit Testing
The existing integration test will validate:
- Script runs without errors (exit code 0)
- Output contains "Basic Usage Example"
- Output contains "Creating MQClient"

### Manual Testing
- Run `python examples/basic_usage.py` directly
- Verify output matches expected format
- Confirm no import or runtime errors

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Analysis

Let me analyze the acceptance criteria for testability:

**1.1 Script displays "Creating MQClient" in output**
- Thoughts: This is testing that when we run the script, specific text appears in stdout. We can test this by running the script and checking the output contains this exact string.
- Testable: yes - example

**1.2 Script displays "Basic Usage Example" in output**
- Thoughts: This is testing that when we run the script, specific text appears in stdout. We can test this by running the script and checking the output contains this exact string.
- Testable: yes - example

**1.3 MQClient creation is logged with "Creating MQClient"**
- Thoughts: This is the same as 1.1, testing that the logging message appears when MQClient is created.
- Testable: yes - example

**1.4 Script demonstrates actual MQClient instantiation**
- Thoughts: This is testing that the script actually creates an MQClient object rather than just showing placeholder text. We can verify this by checking that the script creates an instance and doesn't just print placeholder messages.
- Testable: yes - example

**1.5 Script runs without errors and returns exit code 0**
- Thoughts: This is testing that the script execution is successful. We can test this by running the script and checking the return code.
- Testable: yes - example

### Property Reflection

All the identified testable criteria are examples rather than properties since they test specific, concrete behaviors of a single script execution rather than universal rules that apply across many inputs. The existing integration test already covers these examples appropriately.

### Correctness Properties

Since all acceptance criteria are specific examples rather than universal properties, no additional property-based tests are needed. The existing integration test provides adequate coverage by testing the specific expected behaviors.

## Implementation Plan

1. **Update examples/basic_usage.py**
   - Add "Creating MQClient" print statement
   - Create actual MQClient instance
   - Replace placeholder messages with real functionality
   - Maintain existing header and structure

2. **Verify test passes**
   - Run the specific failing test
   - Confirm output contains expected strings
   - Ensure exit code is 0

This focused approach addresses only the failing test without making unnecessary changes to other parts of the system.
