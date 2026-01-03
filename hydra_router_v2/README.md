# Hydra Router v2

A clean, requirements-based implementation of the ZeroMQ-based message routing system that provides reliable communication between multiple clients and a single server through a centralized routing pattern.

## Features

✅ **Centralized Message Routing** - Routes messages between multiple clients and a single server
✅ **Generic MQClient Library** - Unified interface for both client and server applications
✅ **Automatic Message Format Conversion** - Transparent conversion between ZMQMessage ↔ DRouter formats
✅ **Heartbeat Monitoring** - Automatic client health monitoring and cleanup
✅ **Comprehensive Message Validation** - Detailed error reporting for malformed messages
✅ **Flexible Routing Rules** - Configurable message routing and broadcasting
✅ **Scalable Connection Management** - Support for up to 10 concurrent clients
✅ **Configuration Flexibility** - Configurable network, heartbeat, and logging settings
✅ **Simple Client/Server Examples** - Working examples with proper error handling
✅ **Client Registry Query** - Monitor connected clients and system health
✅ **Comprehensive DEBUG Logging** - Complete message tracing and debugging capabilities
✅ **Integration Tests** - End-to-end validation of message delivery

## Quick Start

### 1. Start the Router

```bash
python -m hydra_router_v2.cli
```

Or with DEBUG logging:

```bash
python -m hydra_router_v2.cli --log-level DEBUG
```

### 2. Start the Server

```bash
python -m hydra_router_v2.simple_server
```

### 3. Start the Client

```bash
python -m hydra_router_v2.simple_client
```

### 4. Run the Demo

```bash
python -m hydra_router_v2.demo
```

## Architecture

### Core Components

- **DRouter** - Message format definitions and constants
- **DMsgType** - Message type enumeration
- **DLog** - Logging configuration constants
- **ZMQMessage** - Internal message format for applications
- **MQClient** - Generic client library with format conversion
- **HydraRouter** - Central router with comprehensive logging
- **SimpleClient/SimpleServer** - Working examples

### Message Flow

```
CLIENT → MQClient.send_message() → ZMQMessage to DRouter conversion
  ↓
ZeroMQ DEALER socket sends JSON to ROUTER
  ↓
HydraRouter receives on ROUTER socket (multipart: [identity, message])
  ↓
Router validates message format and registers client
  ↓
MessageRouter.route_message() based on sender type:
  - Client messages → forwarded to server (if available)
  - Server messages → broadcast to all clients
  ↓
Router sends to targets via ROUTER socket
  ↓
Targets receive on DEALER socket
  ↓
MQClient._receive_loop() processes message
  ↓
Converts DRouter format back to ZMQMessage
  ↓
Calls registered message handler or correlates with pending request
```

## Message Format Conversion

The MQClient automatically converts between internal ZMQMessage format and DRouter format:

**ZMQMessage (Internal)**:
```python
ZMQMessage(
    message_type=DMsgType.SQUARE_REQUEST,
    client_id="client-123",
    request_id="req-456",
    data={"number": 42}
)
```

**DRouter Format (Network)**:
```json
{
    "sender": "SimpleClient",
    "elem": "square_request",
    "timestamp": 1234567890.123,
    "client_id": "client-123",
    "request_id": "req-456",
    "data": {"number": 42}
}
```

## DEBUG Logging

Enable comprehensive DEBUG logging to see complete message tracing:

```bash
# Router with DEBUG logging
python -m hydra_router_v2.cli --log-level DEBUG

# Client with DEBUG logging
python -m hydra_router_v2.simple_client --log-level DEBUG

# Server with DEBUG logging
python -m hydra_router_v2.simple_server --log-level DEBUG
```

DEBUG logging shows:
- Complete message contents (send/receive)
- Message format conversion details
- Routing decisions and message forwarding
- Client registration and heartbeat updates
- Error details and exception information

## Configuration

### Router Configuration

```python
router = HydraRouter(
    router_address="localhost",
    router_port=5556,
    log_level=DLog.DEBUG,
    heartbeat_timeout=30.0,
    max_clients=10,
)
```

### Client Configuration

```python
client = MQClient(
    router_address="tcp://localhost:5556",
    client_type=DRouter.SIMPLE_CLIENT,
    heartbeat_interval=5.0,
    client_id="my-client",
    log_level=DLog.DEBUG,
)
```

## Error Handling

The system provides comprehensive error handling:

- **Connection Errors** - Automatic retry and graceful degradation
- **Message Format Errors** - Detailed validation with specific error messages
- **No Server Connected** - Automatic error responses to clients
- **Timeout Errors** - Configurable timeouts with proper cleanup
- **Exception Printing** - All exceptions printed for debugging (per requirements)

## Testing

Run the integration tests:

```bash
cd hydra_router_v2
python -m pytest tests/test_integration.py -v
```

Tests validate:
- Complete message flow (client → router → server → router → client)
- Message format conversion and content preservation
- Request-response correlation
- Broadcasting to multiple clients
- Error handling and no-server scenarios
- Heartbeat monitoring and client registry

## Examples

### Basic Client Usage

```python
from hydra_router_v2 import MQClient, ZMQMessage, DMsgType, DRouter

async def example_client():
    client = MQClient(
        router_address="tcp://localhost:5556",
        client_type=DRouter.SIMPLE_CLIENT,
    )

    await client.connect()

    # Send request
    message = ZMQMessage(
        message_type=DMsgType.SQUARE_REQUEST,
        data={"number": 42}
    )
    await client.send_message(message)

    await client.disconnect()
```

### Basic Server Usage

```python
from hydra_router_v2 import MQClient, ZMQMessage, DMsgType, DRouter

async def example_server():
    server = MQClient(
        router_address="tcp://localhost:5556",
        client_type=DRouter.SIMPLE_SERVER,
    )

    async def handle_request(message: ZMQMessage):
        # Process request and send response
        data = message.data or {}
        number = data.get("number", 0)
        result = number * number

        response = ZMQMessage(
            message_type=DMsgType.SQUARE_RESPONSE,
            request_id=message.request_id,  # Preserve for correlation
            data={"number": number, "result": result}
        )
        await server.send_message(response)

    await server.connect()
    server.register_message_handler(DMsgType.SQUARE_REQUEST, handle_request)

    # Keep running...
    await asyncio.sleep(3600)
    await server.disconnect()
```

## Requirements Compliance

This implementation fulfills all requirements from the specification:

- ✅ **Requirement 1**: Centralized Message Routing
- ✅ **Requirement 2**: Generic MQClient Library
- ✅ **Requirement 3**: Message Format Standardization and Conversion
- ✅ **Requirement 4**: Heartbeat Monitoring and Client Tracking
- ✅ **Requirement 5**: Comprehensive Message Validation and Error Handling
- ✅ **Requirement 6**: Flexible Routing Rules and Message Broadcasting
- ✅ **Requirement 7**: Scalable Connection Management
- ✅ **Requirement 8**: Configuration and Deployment Flexibility
- ✅ **Requirement 9**: Simple Client and Server Examples
- ✅ **Requirement 10**: Client Registry Query
- ✅ **Requirement 11**: Communication Flow Validation and Debugging

## License

MIT License
