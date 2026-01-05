Examples
========

This section provides practical examples of using Hydra Router.

Basic Echo Server
-----------------

Here's a simple echo server that returns whatever message it receives:

.. literalinclude:: ../../examples/server.py
   :language: python
   :caption: examples/server.py

Basic Client
------------

A simple client that connects to the server and sends messages:

.. literalinclude:: ../../examples/client.py
   :language: python
   :caption: examples/client.py

Heartbeat Example
-----------------

Example of implementing a heartbeat mechanism:

.. literalinclude:: ../../examples/heartbeater.py
   :language: python
   :caption: examples/heartbeater.py

Ping-Pong Pattern
-----------------

Simple ping-pong communication pattern:

Ping client:

.. literalinclude:: ../../examples/ping.py
   :language: python
   :caption: examples/ping.py

Pong server:

.. literalinclude:: ../../examples/pong.py
   :language: python
   :caption: examples/pong.py

Advanced Usage
--------------

For more complex scenarios, you can:

* Implement custom message handlers
* Use different ZeroMQ socket patterns
* Add authentication and security
* Implement load balancing across multiple servers
* Add logging and monitoring
