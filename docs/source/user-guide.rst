User Guide
==========

Command Line Tools
------------------

After installation, two command-line tools are available:

**hydra-ping-client**
    Sends structured ping messages to a pong server

**hydra-pong-server**
    Responds to ping messages with structured pong responses

Basic Usage Examples
--------------------

Start a pong server:

.. code-block:: bash

    # Start server on default port (5757)
    hydra-pong-server

    # Start server on custom port
    hydra-pong-server --port 8080

    # Start server on specific address
    hydra-pong-server --address localhost --port 9000

Send ping messages:

.. code-block:: bash

    # Send single ping to localhost:5757
    hydra-ping-client

    # Send multiple pings with custom interval
    hydra-ping-client --count 10 --interval 0.5

    # Ping remote server with custom message
    hydra-ping-client --hostname 192.168.1.100 --port 8080 --message "Hello Server"

For complete command-line options, use the ``--help`` flag:

.. code-block:: bash

    hydra-ping-client --help
    hydra-pong-server --help