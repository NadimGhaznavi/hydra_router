API Reference
=============

This section provides detailed documentation for all HydraRouter classes and functions.

Core Components
---------------

HydraRouter
~~~~~~~~~~~

.. automodule:: hydra_router.router
   :members:
   :undoc-members:
   :show-inheritance:

MQClient
~~~~~~~~

.. automodule:: hydra_router.mq_client
   :members:
   :undoc-members:
   :show-inheritance:

Router Constants
~~~~~~~~~~~~~~~~

.. automodule:: hydra_router.router_constants
   :members:
   :undoc-members:
   :show-inheritance:

Message Validation
~~~~~~~~~~~~~~~~~~

.. automodule:: hydra_router.validation
   :members:
   :undoc-members:
   :show-inheritance:

Simple Client and Server
-------------------------

Simple Client
~~~~~~~~~~~~~

.. automodule:: hydra_router.simple_client
   :members:
   :undoc-members:
   :show-inheritance:

Simple Server
~~~~~~~~~~~~~

.. automodule:: hydra_router.simple_server
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
----------

.. automodule:: hydra_router.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

Logging Configuration
---------------------

.. automodule:: hydra_router.logging_config
   :members:
   :undoc-members:
   :show-inheritance:

Command Line Interface
----------------------

.. automodule:: hydra_router.cli
   :members:
   :undoc-members:
   :show-inheritance:

Message Types and Data Structures
----------------------------------

ZMQMessage
~~~~~~~~~~

The ZMQMessage class represents a message in the HydraRouter system:

.. code-block:: python

   from hydra_router.mq_client import ZMQMessage, MessageType

   message = ZMQMessage(
       message_type=MessageType.SQUARE_REQUEST,
       timestamp=time.time(),
       client_id="my-client",
       request_id="req-123",
       data={"number": 5}
   )

MessageType Enumeration
~~~~~~~~~~~~~~~~~~~~~~~

Available message types:

* ``MessageType.SQUARE_REQUEST`` - Request to calculate a square
* ``MessageType.SQUARE_RESPONSE`` - Response with calculated square
* ``MessageType.HEARTBEAT`` - Keep-alive message
* ``MessageType.CLIENT_REGISTRY_REQUEST`` - Request client registry info
* ``MessageType.CLIENT_REGISTRY_RESPONSE`` - Client registry information
* ``MessageType.ERROR`` - Error message

Client Types
~~~~~~~~~~~~

Supported client types from RouterConstants:

* ``RouterConstants.HYDRA_CLIENT`` - Standard client
* ``RouterConstants.HYDRA_SERVER`` - Standard server
* ``RouterConstants.SIMPLE_CLIENT`` - Simple calculation client
* ``RouterConstants.SIMPLE_SERVER`` - Simple calculation server

Usage Examples
--------------

Basic Client Usage
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from hydra_router.mq_client import MQClient, MessageType, ZMQMessage
   from hydra_router.router_constants import RouterConstants

   async def example_client():
       client = MQClient(
           router_address="tcp://localhost:5556",
           client_type=RouterConstants.HYDRA_CLIENT,
           client_id="example-client"
       )

       try:
           await client.connect()

           # Send a message
           message = ZMQMessage(
               message_type=MessageType.SQUARE_REQUEST,
               timestamp=time.time(),
               client_id="example-client",
               data={"number": 5}
           )

           await client.send_message(message)

       finally:
           await client.disconnect()

Custom Message Handler
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def handle_response(message):
       print(f"Received: {message.data}")

   client.register_message_handler(MessageType.SQUARE_RESPONSE, handle_response)

Router Startup
~~~~~~~~~~~~~~

.. code-block:: python

   from hydra_router.router import HydraRouter

   async def start_router():
       router = HydraRouter(address="0.0.0.0", port=5556)
       await router.start()

       try:
           # Keep router running
           while True:
               await asyncio.sleep(1)
       finally:
           await router.stop()

Error Handling
~~~~~~~~~~~~~~

.. code-block:: python

   from hydra_router.exceptions import HydraRouterError, ConnectionError

   try:
       await client.connect()
   except ConnectionError as e:
       print(f"Connection failed: {e}")
   except HydraRouterError as e:
       print(f"Router error: {e}")

Configuration Examples
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Custom client configuration
   client = MQClient(
       router_address="tcp://192.168.1.100:5557",
       client_type="CUSTOM_CLIENT",
       client_id="specialized-client"
   )

   # Router with custom settings
   router = HydraRouter(
       address="0.0.0.0",
       port=5557
   )

Type Hints
----------

HydraRouter uses comprehensive type hints for better IDE support and code clarity:

.. code-block:: python

   from typing import Optional, Dict, Any, List
   from hydra_router.mq_client import MQClient, ZMQMessage

   async def send_request(
       client: MQClient,
       data: Dict[str, Any]
   ) -> Optional[ZMQMessage]:
       # Implementation here
       pass
