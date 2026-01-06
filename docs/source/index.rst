Hydra Router documentation
==========================

The **Hydra Router** project implements a ZeroMQ-based distributed computing architecture with a ping-pong messaging system.

Hydra Router provides abstract base classes for building distributed clients and servers, along with concrete implementations for ping-pong communication patterns. The framework uses structured messaging via the HydraMsg protocol for reliable communication between distributed components.

Key Features
------------

* **Abstract Base Classes**: Extensible HydraClient and HydraServer base classes
* **Structured Messaging**: JSON-based HydraMsg protocol for reliable communication
* **Ping-Pong Implementation**: Ready-to-use ping client and pong server
* **ZeroMQ Backend**: High-performance messaging using ZeroMQ
* **Command Line Tools**: Easy-to-use executables for testing and development

Quick Start
-----------

Install Hydra Router and start using the ping-pong system:

.. code-block:: bash

    # Install the package
    pip install hydra-router

    # Start a pong server (in one terminal)
    hydra-pong-server

    # Send pings from a client (in another terminal)
    hydra-ping-client --count 5

Architecture
------------

Hydra Router follows an abstract base class pattern:

* **HydraClient**: Abstract base class for all client implementations
* **HydraClientPing**: Concrete ping client that sends structured ping messages
* **HydraServer**: Abstract base class for all server implementations  
* **HydraServerPong**: Concrete pong server that responds to ping messages

All communication uses the HydraMsg protocol for structured, reliable messaging between components.

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    installation.rst
    api/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
