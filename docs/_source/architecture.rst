Architecture Overview
=====================

HydraRouter is designed as a high-performance, scalable message routing system built on ZeroMQ. This document explains the core architectural concepts and design decisions.

System Components
-----------------

HydraRouter consists of several key components:

**System Architecture**::

   ┌─────────────────────────────────────────┐
   │            HydraRouter System           │
   │  ┌─────────────┐  ┌─────────────────┐   │
   │  │   Router    │  │ Client Registry │   │
   │  │    Core     │  │                 │   │
   │  └─────────────┘  └─────────────────┘   │
   │  ┌─────────────┐  ┌─────────────────┐   │
   │  │  Message    │  │    Message      │   │
   │  │   Router    │  │   Validator     │   │
   │  └─────────────┘  └─────────────────┘   │
   └─────────────────────────────────────────┘
              ▲                    ▲
              │                    │
   ┌──────────┴──────────┐ ┌──────┴──────────┐
   │      Clients        │ │     Servers     │
   │ ┌─────────────────┐ │ │ ┌─────────────┐ │
   │ │ Simple Client   │ │ │ │Simple Server│ │
   │ │ Hydra Client    │ │ │ │Hydra Server │ │
   │ │ Custom Client   │ │ │ │Custom Server│ │
   │ └─────────────────┘ │ │ └─────────────┘ │
   └─────────────────────┘ └─────────────────┘

Core Components
~~~~~~~~~~~~~~~

**HydraRouter Core**
   The central message broker that manages all client connections and routes messages between clients and servers. Built on ZeroMQ ROUTER sockets for high performance.

**Client Registry**
   Maintains a registry of all connected clients and servers, including their types, connection status, and heartbeat information. Provides automatic cleanup of inactive clients.

**Message Router**
   Handles the routing logic for different message types. Routes client requests to appropriate servers and broadcasts server responses to relevant clients.

**Message Validator**
   Validates all incoming messages against the RouterConstants format specification. Ensures message integrity and provides detailed error reporting.

**MQClient Library**
   Generic client library that handles connection management, message format conversion, and provides a unified interface for both client and server applications.

Message Flow
------------

The message flow in HydraRouter follows a hub-and-spoke pattern:

1. **Client Connection**: Clients connect to the router using ZeroMQ DEALER sockets
2. **Registration**: Clients register with the router, specifying their type and ID
3. **Message Routing**: The router routes messages based on client types and message content
4. **Response Handling**: Responses are routed back to the appropriate clients
5. **Heartbeat Management**: Clients send periodic heartbeats to maintain their registration

Message Types
~~~~~~~~~~~~~

HydraRouter supports several message types:

* **SQUARE_REQUEST**: Request to calculate the square of a number
* **SQUARE_RESPONSE**: Response containing the calculated square
* **HEARTBEAT**: Keep-alive message to maintain client registration
* **CLIENT_REGISTRY_REQUEST**: Request for information about connected clients
* **CLIENT_REGISTRY_RESPONSE**: Response with client registry information

Client Types
~~~~~~~~~~~~

The system supports multiple client types:

* **HYDRA_CLIENT**: Standard client for general-purpose communication
* **HYDRA_SERVER**: Standard server for processing requests
* **SIMPLE_CLIENT**: Simplified client for basic square calculations
* **SIMPLE_SERVER**: Simplified server for processing square requests
* **Custom Types**: Extensible system allows for custom client types

Message Format
--------------

All messages follow the RouterConstants format specification:

.. code-block:: python

   {
       "sender": "client-id",           # Client identifier
       "elem": "SQUARE_REQUEST",        # Message type
       "timestamp": 1640995200.0,       # Unix timestamp
       "data": {"number": 5},           # Message payload
       "request_id": "req-123"          # Optional request correlation ID
   }

The MQClient library automatically converts between this format and the internal ZMQMessage format.

Scalability Design
------------------

HydraRouter is designed for high scalability:

**Asynchronous Processing**
   All operations are asynchronous using Python's asyncio, allowing for high concurrency without blocking.

**ZeroMQ Performance**
   Built on ZeroMQ for maximum throughput and minimal latency. ZeroMQ handles the low-level networking efficiently.

**Stateless Design**
   The router maintains minimal state, making it easy to scale horizontally if needed.

**Efficient Message Routing**
   Messages are routed directly without unnecessary copying or transformation.

**Connection Pooling**
   Clients maintain persistent connections to reduce connection overhead.

Error Handling
--------------

HydraRouter implements comprehensive error handling:

**Message Validation**
   All messages are validated against the specification before processing. Invalid messages are rejected with detailed error information.

**Connection Management**
   Automatic detection and cleanup of failed connections. Clients can reconnect seamlessly.

**Graceful Degradation**
   The system continues operating even when individual clients fail or disconnect.

**Comprehensive Logging**
   Detailed logging at multiple levels for debugging and monitoring.

**Exception Hierarchy**
   Custom exception types for different error conditions, making error handling more precise.

Security Considerations
-----------------------

**Network Security**
   HydraRouter operates at the application layer and relies on network-level security (VPNs, firewalls, etc.) for protection.

**Message Validation**
   All messages are validated to prevent malformed data from affecting the system.

**Client Authentication**
   Basic client identification through client IDs. More advanced authentication can be implemented at the application level.

**Resource Limits**
   Automatic cleanup of inactive clients prevents resource exhaustion.

Performance Characteristics
---------------------------

**Throughput**
   Designed to handle thousands of messages per second with minimal latency.

**Memory Usage**
   Efficient memory usage with automatic cleanup of inactive connections.

**CPU Usage**
   Minimal CPU overhead due to ZeroMQ's efficient implementation and asynchronous design.

**Scalability**
   Supports hundreds of concurrent client connections on standard hardware.

Extension Points
----------------

HydraRouter is designed to be extensible:

**Custom Client Types**
   Easy to add new client types by extending the RouterConstants and implementing custom message handlers.

**Custom Message Types**
   New message types can be added to support different application requirements.

**Custom Routing Logic**
   The message routing logic can be extended to support more complex routing scenarios.

**Monitoring Integration**
   Hooks for integrating with monitoring and metrics systems.

**Protocol Extensions**
   The message format can be extended while maintaining backward compatibility.

Deployment Patterns
-------------------

**Single Router**
   Simple deployment with one router instance for small to medium applications.

**Load Balanced**
   Multiple router instances behind a load balancer for high availability.

**Federated**
   Multiple routers connected together for geographic distribution.

**Containerized**
   Docker containers for easy deployment and scaling in container orchestration systems.

This architecture provides a solid foundation for building scalable, distributed applications while maintaining simplicity and performance.
