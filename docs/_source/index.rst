Hydra Router documentation
==========================

The **Hydra Router** project implements a ZeroMQ-based distributed computing architecture
with a ping-pong messaging system.

Hydra Router provides abstract base classes for building distributed clients and servers,
along with a concrete reference (ping/pong) implementation. The framework uses structured
messaging via the HydraMsg protocol for reliable communication between distributed
components.

Key Features
------------

* **Abstract Base Classes**: Extensible HydraClient and HydraServer base classes
* **Structured Messaging**: JSON-based HydraMsg protocol for reliable communication
* **Ping-Pong Implementation**: Ready-to-use ping client and pong server
* **ZeroMQ Backend**: High-performance messaging using ZeroMQ
* **Command Line Tools**: Easy-to-use executables for testing and development


.. toctree::
    :maxdepth: 2
    :caption: Contents:

    installation.rst
    quickstart.rst
    user-guide.rst
    architecture.rst

    DHydra.rst
    HydraClient.rst
    HydraClientPing.rst
    HydraLog.rst
    HydraMsg.rst
    HydraServer.rst
    HydraServerPong.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
