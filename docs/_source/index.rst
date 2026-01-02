HydraRouter Documentation
=========================

Welcome to HydraRouter, a high-performance ZeroMQ-based message routing system designed for distributed applications. HydraRouter provides a robust, scalable solution for client-server communication with support for multiple client types and advanced message routing capabilities.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   architecture
   deployment
   configuration
   api_reference
   examples
   troubleshooting

Quick Start
-----------

Install HydraRouter via pip:

.. code-block:: bash

   pip install hydra-router

Start the router:

.. code-block:: bash

   hydra-router start --address 0.0.0.0 --port 5556

Create a simple client:

.. code-block:: python

   import asyncio
   from hydra_router.simple_client import SimpleClient

   async def main():
       client = SimpleClient()
       await client.start()
       await client.send_square_request(5)
       await client.stop()

   asyncio.run(main())

Features
--------

* **High Performance**: Built on ZeroMQ for maximum throughput and minimal latency
* **Scalable Architecture**: Support for multiple concurrent clients and servers
* **Type Safety**: Comprehensive message validation and error handling
* **Extensible**: Easy to add custom client types and message handlers
* **Production Ready**: Comprehensive testing with property-based validation
* **Easy Deployment**: Simple CLI for router management and configuration

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
