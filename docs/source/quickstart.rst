Quick Start
===========

This guide will help you get started with Hydra Router quickly.

Basic Server Example
--------------------

Create a simple server that echoes messages:

.. code-block:: python

    from hydra_router.server.HydraServer import HydraServer

    def echo_handler(message):
        """Simple echo handler that returns the received message."""
        return f"Echo: {message}"

    # Create and start server
    server = HydraServer(port=5555)
    server.start(echo_handler)

Basic Client Example
--------------------

Create a client to send messages to the server:

.. code-block:: python

    from hydra_router.client.HydraClient import HydraClient

    # Create client and connect to server
    client = HydraClient(server_hostname="localhost", server_port=5555)

    # Send a message
    response = client.send_message("Hello, Server!")
    print(response)  # Output: Echo: Hello, Server!

    # Clean up
    client.close()

Command Line Usage
------------------

You can also run the server and client from the command line:

Start a server:

.. code-block:: bash

    hydra-server --port 5555

Connect with a client:

.. code-block:: bash

    hydra-client --hostname localhost --port 5555

Next Steps
----------

* Check out the :doc:`api/index` for detailed API documentation
* Look at the :doc:`examples` for more complex usage patterns
* Read about the architecture and design patterns in the full documentation
