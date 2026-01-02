Getting Started
===============

This guide will help you get up and running with HydraRouter quickly.

Installation
------------

HydraRouter requires Python 3.11 or later. Install it using pip:

.. code-block:: bash

   pip install hydra-router

For development, you can install from source:

.. code-block:: bash

   git clone https://github.com/NadimGhaznavi/hydra_router.git
   cd hydra_router
   pip install -e .

Starting the Router
-------------------

The HydraRouter acts as a central message broker. Start it using the CLI:

.. code-block:: bash

   # Start with default settings (localhost:5556)
   hydra-router start

   # Start with custom address and port
   hydra-router start --address 0.0.0.0 --port 5557

   # Start with debug logging
   hydra-router start --log-level DEBUG

The router will start and listen for client connections. You should see output like:

.. code-block:: text

   🚀 Starting HydraRouter...
      Address: 0.0.0.0
      Port: 5556
      Log Level: INFO

   ✅ HydraRouter started successfully!
      Listening on: tcp://0.0.0.0:5556
      Press Ctrl+C to stop

Basic Usage
-----------

Simple Client Example
~~~~~~~~~~~~~~~~~~~~~

Create a simple client that sends square calculation requests:

.. code-block:: python

   import asyncio
   from hydra_router.simple_client import SimpleClient

   async def main():
       # Create client
       client = SimpleClient(
           router_address="tcp://localhost:5556",
           client_id="my-client"
       )

       try:
           # Connect to router
           await client.start()

           # Send square requests
           await client.send_square_request(5)
           await client.send_square_request(10)

           # Wait for responses
           await asyncio.sleep(2)

       finally:
           # Clean shutdown
           await client.stop()

   if __name__ == "__main__":
       asyncio.run(main())

Simple Server Example
~~~~~~~~~~~~~~~~~~~~~

Create a simple server that processes square calculation requests:

.. code-block:: python

   import asyncio
   from hydra_router.simple_server import SimpleServer

   async def main():
       # Create server
       server = SimpleServer(
           router_address="tcp://localhost:5556",
           server_id="my-server"
       )

       try:
           # Connect to router
           await server.start()

           # Run server (will process requests until interrupted)
           await server.run()

       except KeyboardInterrupt:
           print("Server interrupted")
       finally:
           # Clean shutdown
           await server.stop()

   if __name__ == "__main__":
       asyncio.run(main())

Interactive Client
~~~~~~~~~~~~~~~~~~

For quick testing, use the interactive client:

.. code-block:: bash

   hydra-client-simple

This will start an interactive session where you can enter numbers to calculate their squares.

Interactive Server
~~~~~~~~~~~~~~~~~~

Start a simple server:

.. code-block:: bash

   hydra-server-simple

The server will process square calculation requests from any connected clients.

Configuration Options
---------------------

Router Configuration
~~~~~~~~~~~~~~~~~~~~

The router supports various configuration options:

.. code-block:: bash

   hydra-router start \
       --address 0.0.0.0 \        # Bind address (default: 127.0.0.1)
       --port 5556 \              # Bind port (default: 5556)
       --log-level INFO           # Logging level (DEBUG, INFO, WARNING, ERROR)

Client Configuration
~~~~~~~~~~~~~~~~~~~~

Clients can be configured with various options:

.. code-block:: python

   from hydra_router.mq_client import MQClient
   from hydra_router.router_constants import RouterConstants

   client = MQClient(
       router_address="tcp://localhost:5556",  # Router address
       client_type=RouterConstants.HYDRA_CLIENT,  # Client type
       client_id="unique-client-id"  # Unique identifier
   )

Network Configurations
~~~~~~~~~~~~~~~~~~~~~~

HydraRouter supports various network configurations:

* **Local development**: ``tcp://localhost:5556``
* **Network accessible**: ``tcp://0.0.0.0:5556``
* **Specific interface**: ``tcp://192.168.1.100:5556``
* **Unix socket**: ``ipc:///tmp/hydra-router.sock`` (Linux/macOS only)

Next Steps
----------

* Read the :doc:`architecture` guide to understand how HydraRouter works
* Explore the :doc:`examples` for more advanced usage patterns
* Check the :doc:`api_reference` for detailed API documentation
* See :doc:`troubleshooting` if you encounter issues
