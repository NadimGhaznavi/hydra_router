Examples
========

This section provides comprehensive examples demonstrating various HydraRouter usage patterns.

Basic Examples
--------------

Simple Square Calculator
~~~~~~~~~~~~~~~~~~~~~~~~~

The most basic example shows a client requesting square calculations from a server:

.. literalinclude:: ../../examples/basic_client_server.py
   :language: python
   :caption: Basic Client-Server Communication

To run this example:

1. Start the router: ``hydra-router start``
2. Run the example: ``python examples/basic_client_server.py``

Multiple Clients
~~~~~~~~~~~~~~~~

This example demonstrates how multiple clients can connect simultaneously:

.. literalinclude:: ../../examples/multiple_clients.py
   :language: python
   :caption: Multiple Clients Example
   :lines: 1-50

The example creates multiple clients that send requests concurrently, showing how the router handles multiple connections.

Advanced Examples
-----------------

Custom Client Types
~~~~~~~~~~~~~~~~~~~

Create custom client and server types with specialized functionality:

.. literalinclude:: ../../examples/custom_client_type.py
   :language: python
   :caption: Custom Client Types
   :lines: 1-100

This example shows:

* Custom client types (MATH_CLIENT, MATH_SERVER)
* Extended mathematical operations beyond squares
* Custom message handling patterns
* Specialized client-server communication

Error Handling
~~~~~~~~~~~~~~

Comprehensive error handling and recovery scenarios:

.. literalinclude:: ../../examples/error_handling.py
   :language: python
   :caption: Error Handling Example
   :lines: 1-80

This example demonstrates:

* Connection failure handling
* Invalid message processing
* Client reconnection scenarios
* Server error handling
* Timeout management

Configuration Examples
----------------------

Network Configurations
~~~~~~~~~~~~~~~~~~~~~~

Different network configuration patterns:

.. literalinclude:: ../../examples/configuration_example.py
   :language: python
   :caption: Configuration Examples

Router Configuration
~~~~~~~~~~~~~~~~~~~~

Starting the router with different configurations:

.. code-block:: bash

   # Local development
   hydra-router start

   # Network accessible
   hydra-router start --address 0.0.0.0 --port 5556

   # Debug mode
   hydra-router start --log-level DEBUG

   # Custom port
   hydra-router start --port 5557

Client Configuration
~~~~~~~~~~~~~~~~~~~~

Configuring clients for different scenarios:

.. code-block:: python

   # Standard client
   client = MQClient(
       router_address="tcp://localhost:5556",
       client_type=RouterConstants.HYDRA_CLIENT,
       client_id="standard-client"
   )

   # Remote router
   client = MQClient(
       router_address="tcp://192.168.1.100:5556",
       client_type=RouterConstants.SIMPLE_CLIENT,
       client_id="remote-client"
   )

   # Unix socket (Linux/macOS)
   client = MQClient(
       router_address="ipc:///tmp/hydra-router.sock",
       client_type=RouterConstants.HYDRA_CLIENT,
       client_id="unix-client"
   )

Interactive Examples
--------------------

Interactive Client
~~~~~~~~~~~~~~~~~~

Use the built-in interactive client for testing:

.. code-block:: bash

   # Start interactive client
   hydra-client-simple

   # Connect to specific router
   hydra-client-simple --router-address tcp://192.168.1.100:5556

   # Send single request
   hydra-client-simple --number 42

Interactive Server
~~~~~~~~~~~~~~~~~~

Start a simple server for processing requests:

.. code-block:: bash

   # Start simple server
   hydra-server-simple

   # Server with statistics
   hydra-server-simple --stats

   # Connect to specific router
   hydra-server-simple --router-address tcp://192.168.1.100:5556

Complete Demo
~~~~~~~~~~~~~

Run the complete interactive demo:

.. literalinclude:: ../../examples/simple_square_demo.py
   :language: python
   :caption: Complete Interactive Demo
   :lines: 1-50

Production Examples
-------------------

Deployment Patterns
~~~~~~~~~~~~~~~~~~~

**Single Router Deployment**

.. code-block:: python

   # production_router.py
   import asyncio
   import signal
   from hydra_router.router import HydraRouter
   from hydra_router.logging_config import setup_logging

   async def main():
       setup_logging(__name__, level="INFO")

       router = HydraRouter(address="0.0.0.0", port=5556)

       # Graceful shutdown handling
       def signal_handler(signum, frame):
           print(f"Received signal {signum}, shutting down...")
           router.running = False

       signal.signal(signal.SIGINT, signal_handler)
       signal.signal(signal.SIGTERM, signal_handler)

       try:
           await router.start()
           while router.running:
               await asyncio.sleep(1)
       finally:
           await router.stop()

   if __name__ == "__main__":
       asyncio.run(main())

**High-Availability Client**

.. code-block:: python

   # ha_client.py
   import asyncio
   import time
   from hydra_router.mq_client import MQClient, MessageType, ZMQMessage
   from hydra_router.router_constants import RouterConstants

   class HAClient:
       def __init__(self, router_addresses):
           self.router_addresses = router_addresses
           self.current_router = 0
           self.client = None

       async def connect_with_failover(self):
           for i, address in enumerate(self.router_addresses):
               try:
                   self.client = MQClient(
                       router_address=address,
                       client_type=RouterConstants.HYDRA_CLIENT,
                       client_id=f"ha-client-{int(time.time())}"
                   )
                   await self.client.connect()
                   self.current_router = i
                   return True
               except Exception as e:
                   print(f"Failed to connect to {address}: {e}")
                   continue
           return False

Monitoring and Metrics
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # monitoring_client.py
   import asyncio
   import time
   from hydra_router.mq_client import MQClient, MessageType, ZMQMessage
   from hydra_router.router_constants import RouterConstants

   class MonitoringClient:
       def __init__(self):
           self.client = MQClient(
               router_address="tcp://localhost:5556",
               client_type="MONITORING_CLIENT",
               client_id="monitor"
           )
           self.metrics = {
               'messages_sent': 0,
               'messages_received': 0,
               'errors': 0
           }

       async def collect_metrics(self):
           while True:
               # Request client registry information
               message = ZMQMessage(
                   message_type=MessageType.CLIENT_REGISTRY_REQUEST,
                   timestamp=time.time(),
                   client_id="monitor"
               )

               await self.client.send_message(message)
               await asyncio.sleep(30)  # Collect every 30 seconds

Testing Examples
----------------

Unit Testing
~~~~~~~~~~~~

.. code-block:: python

   # test_client.py
   import pytest
   import asyncio
   from unittest.mock import AsyncMock, patch
   from hydra_router.mq_client import MQClient
   from hydra_router.router_constants import RouterConstants

   @pytest.mark.asyncio
   async def test_client_connection():
       with patch('hydra_router.mq_client.zmq.asyncio.Context') as mock_context:
           mock_socket = AsyncMock()
           mock_context.return_value.socket.return_value = mock_socket

           client = MQClient(
               router_address="tcp://localhost:5556",
               client_type=RouterConstants.HYDRA_CLIENT,
               client_id="test-client"
           )

           await client.connect()
           assert client.connected

           await client.disconnect()
           assert not client.connected

Integration Testing
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # test_integration.py
   import pytest
   import asyncio
   from hydra_router.router import HydraRouter
   from hydra_router.simple_client import SimpleClient
   from hydra_router.simple_server import SimpleServer

   @pytest.mark.asyncio
   async def test_full_system():
       # Start router
       router = HydraRouter(address="127.0.0.1", port=5557)
       await router.start()

       try:
           # Start server
           server = SimpleServer(router_address="tcp://127.0.0.1:5557")
           await server.start()

           # Start client
           client = SimpleClient(router_address="tcp://127.0.0.1:5557")
           await client.start()

           # Send request
           await client.send_square_request(5)

           # Wait for processing
           await asyncio.sleep(1)

           # Cleanup
           await client.stop()
           await server.stop()

       finally:
           await router.stop()

Performance Testing
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # performance_test.py
   import asyncio
   import time
   from hydra_router.mq_client import MQClient, MessageType, ZMQMessage
   from hydra_router.router_constants import RouterConstants

   async def performance_test():
       client = MQClient(
           router_address="tcp://localhost:5556",
           client_type=RouterConstants.HYDRA_CLIENT,
           client_id="perf-test"
       )

       await client.connect()

       # Send 1000 messages and measure time
       start_time = time.time()

       for i in range(1000):
           message = ZMQMessage(
               message_type=MessageType.SQUARE_REQUEST,
               timestamp=time.time(),
               client_id="perf-test",
               request_id=f"perf-{i}",
               data={"number": i}
           )
           await client.send_message(message)

       end_time = time.time()
       duration = end_time - start_time
       rate = 1000 / duration

       print(f"Sent 1000 messages in {duration:.2f}s ({rate:.2f} msg/s)")

       await client.disconnect()

Best Practices
--------------

Connection Management
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Always use proper connection lifecycle
   async def proper_client_usage():
       client = MQClient(...)

       try:
           await client.connect()
           # Do work here
       finally:
           await client.disconnect()

   # Or use as async context manager (if implemented)
   async def context_manager_usage():
       async with MQClient(...) as client:
           # Client is automatically connected and disconnected
           pass

Error Handling
~~~~~~~~~~~~~~

.. code-block:: python

   from hydra_router.exceptions import (
       HydraRouterError,
       ConnectionError,
       MessageValidationError
   )

   try:
       await client.send_message(message)
   except ConnectionError:
       # Handle connection issues
       await reconnect_client()
   except MessageValidationError:
       # Handle invalid message format
       log_validation_error()
   except HydraRouterError:
       # Handle other router errors
       handle_router_error()

Message Handling
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Register handlers for different message types
   def handle_response(message):
       # Process response
       pass

   def handle_error(message):
       # Handle error message
       pass

   client.register_message_handler(MessageType.SQUARE_RESPONSE, handle_response)
   client.register_message_handler(MessageType.ERROR, handle_error)

These examples provide a comprehensive guide to using HydraRouter in various scenarios, from simple demonstrations to production deployments.
