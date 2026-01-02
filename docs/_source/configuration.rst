Configuration Guide
===================

This guide covers configuring HydraRouter for different environments and use cases.

Router Configuration
--------------------

Command Line Options
~~~~~~~~~~~~~~~~~~~~

The router can be configured using command-line arguments:

.. code-block:: bash

   hydra-router start \
       --address 0.0.0.0 \        # Bind address
       --port 5556 \              # Bind port
       --log-level INFO           # Logging level

Available options:

* ``--address``: IP address to bind to (default: 127.0.0.1)
* ``--port``: Port number to bind to (default: 5556)
* ``--log-level``: Logging level (DEBUG, INFO, WARNING, ERROR)

Programmatic Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure the router programmatically:

.. code-block:: python

   from hydra_router.router import HydraRouter
   from hydra_router.logging_config import setup_logging

   # Configure logging
   setup_logging(__name__, level="INFO")

   # Create router with custom settings
   router = HydraRouter(
       address="0.0.0.0",
       port=5556
   )

   # Start router
   await router.start()

Network Configuration
---------------------

Local Development
~~~~~~~~~~~~~~~~~

For local development and testing:

.. code-block:: bash

   # Bind to localhost only
   hydra-router start --address 127.0.0.1 --port 5556

   # Client connection
   client_address = "tcp://localhost:5556"

Network Accessible
~~~~~~~~~~~~~~~~~~

For network-accessible deployment:

.. code-block:: bash

   # Bind to all interfaces
   hydra-router start --address 0.0.0.0 --port 5556

   # Clients connect using server IP
   client_address = "tcp://192.168.1.100:5556"

Specific Interface
~~~~~~~~~~~~~~~~~~

Bind to a specific network interface:

.. code-block:: bash

   # Bind to specific IP
   hydra-router start --address 192.168.1.100 --port 5556

Unix Domain Sockets
~~~~~~~~~~~~~~~~~~~

For local communication on Unix systems:

.. code-block:: python

   # Router configuration
   router = HydraRouter(address="ipc:///tmp/hydra-router.sock")

   # Client configuration
   client = MQClient(
       router_address="ipc:///tmp/hydra-router.sock",
       client_type=RouterConstants.HYDRA_CLIENT,
       client_id="unix-client"
   )

Client Configuration
--------------------

Basic Client Setup
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from hydra_router.mq_client import MQClient
   from hydra_router.router_constants import RouterConstants

   client = MQClient(
       router_address="tcp://localhost:5556",
       client_type=RouterConstants.HYDRA_CLIENT,
       client_id="my-client"
   )

Client Types
~~~~~~~~~~~~

Different client types for different purposes:

.. code-block:: python

   # Standard client for general communication
   standard_client = MQClient(
       router_address="tcp://localhost:5556",
       client_type=RouterConstants.HYDRA_CLIENT,
       client_id="standard-client"
   )

   # Simple client for basic calculations
   simple_client = MQClient(
       router_address="tcp://localhost:5556",
       client_type=RouterConstants.SIMPLE_CLIENT,
       client_id="calc-client"
   )

   # Server for processing requests
   server = MQClient(
       router_address="tcp://localhost:5556",
       client_type=RouterConstants.HYDRA_SERVER,
       client_id="processing-server"
   )

   # Custom client type
   custom_client = MQClient(
       router_address="tcp://localhost:5556",
       client_type="CUSTOM_CLIENT_TYPE",
       client_id="specialized-client"
   )

Connection Management
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Basic connection
   await client.connect()
   # ... do work ...
   await client.disconnect()

   # Connection with error handling
   try:
       await client.connect()
       # ... do work ...
   except ConnectionError as e:
       print(f"Connection failed: {e}")
   finally:
       if client.connected:
           await client.disconnect()

Logging Configuration
---------------------

Basic Logging Setup
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from hydra_router.logging_config import setup_logging

   # Basic setup
   setup_logging(__name__)

   # Custom log level
   setup_logging(__name__, level="DEBUG")

   # File logging
   setup_logging(__name__, level="INFO", log_file="hydra-router.log")

Advanced Logging
~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging
   from hydra_router.logging_config import get_logging_config

   # Get default configuration
   config = get_logging_config(level="INFO")

   # Customize configuration
   config['handlers']['file'] = {
       'class': 'logging.handlers.RotatingFileHandler',
       'filename': '/var/log/hydra-router.log',
       'maxBytes': 10485760,  # 10MB
       'backupCount': 5,
       'formatter': 'detailed'
   }

   # Apply configuration
   logging.config.dictConfig(config)

Production Configuration
------------------------

High Availability Setup
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # production_router.py
   import asyncio
   import signal
   import sys
   from hydra_router.router import HydraRouter
   from hydra_router.logging_config import setup_logging

   async def main():
       # Production logging
       setup_logging(__name__, level="INFO", log_file="/var/log/hydra-router.log")

       # Production router
       router = HydraRouter(
           address="0.0.0.0",
           port=5556
       )

       # Graceful shutdown handling
       def signal_handler(signum, frame):
           print(f"Received signal {signum}, shutting down gracefully...")
           router.running = False

       signal.signal(signal.SIGINT, signal_handler)
       signal.signal(signal.SIGTERM, signal_handler)

       try:
           await router.start()
           print("HydraRouter started in production mode")

           while router.running:
               await asyncio.sleep(1)

       except Exception as e:
           print(f"Router error: {e}")
           sys.exit(1)
       finally:
           await router.stop()
           print("HydraRouter stopped")

   if __name__ == "__main__":
       asyncio.run(main())

Load Balancer Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For multiple router instances behind a load balancer:

.. code-block:: yaml

   # nginx.conf
   upstream hydra_routers {
       server 192.168.1.10:5556;
       server 192.168.1.11:5556;
       server 192.168.1.12:5556;
   }

   server {
       listen 5556;
       proxy_pass hydra_routers;
   }

Environment Variables
---------------------

Configure using environment variables:

.. code-block:: bash

   # Set environment variables
   export HYDRA_ROUTER_ADDRESS="0.0.0.0"
   export HYDRA_ROUTER_PORT="5556"
   export HYDRA_ROUTER_LOG_LEVEL="INFO"

.. code-block:: python

   import os
   from hydra_router.router import HydraRouter

   # Use environment variables
   router = HydraRouter(
       address=os.getenv("HYDRA_ROUTER_ADDRESS", "127.0.0.1"),
       port=int(os.getenv("HYDRA_ROUTER_PORT", "5556"))
   )

Configuration Files
-------------------

YAML Configuration
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # hydra-router.yaml
   router:
     address: "0.0.0.0"
     port: 5556

   logging:
     level: "INFO"
     file: "/var/log/hydra-router.log"

   clients:
     timeout: 300  # seconds
     max_connections: 1000

.. code-block:: python

   import yaml
   from hydra_router.router import HydraRouter

   # Load configuration
   with open("hydra-router.yaml", "r") as f:
       config = yaml.safe_load(f)

   # Create router from config
   router = HydraRouter(
       address=config["router"]["address"],
       port=config["router"]["port"]
   )

JSON Configuration
~~~~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "router": {
       "address": "0.0.0.0",
       "port": 5556
     },
     "logging": {
       "level": "INFO",
       "file": "/var/log/hydra-router.log"
     }
   }

Security Configuration
----------------------

Network Security
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Firewall configuration (iptables)
   sudo iptables -A INPUT -p tcp --dport 5556 -s 192.168.1.0/24 -j ACCEPT
   sudo iptables -A INPUT -p tcp --dport 5556 -j DROP

   # UFW (Ubuntu)
   sudo ufw allow from 192.168.1.0/24 to any port 5556

Client Authentication
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Basic client identification
   client = MQClient(
       router_address="tcp://localhost:5556",
       client_type=RouterConstants.HYDRA_CLIENT,
       client_id="authenticated-client-12345"  # Unique, authenticated ID
   )

   # Custom authentication in message data
   message = ZMQMessage(
       message_type=MessageType.SQUARE_REQUEST,
       timestamp=time.time(),
       client_id="authenticated-client-12345",
       data={
           "auth_token": "your-auth-token",
           "number": 5
       }
   )

Performance Configuration
-------------------------

System Limits
~~~~~~~~~~~~~~

.. code-block:: bash

   # Increase file descriptor limits
   echo "* soft nofile 65536" >> /etc/security/limits.conf
   echo "* hard nofile 65536" >> /etc/security/limits.conf

   # Network buffer sizes
   echo "net.core.rmem_max = 134217728" >> /etc/sysctl.conf
   echo "net.core.wmem_max = 134217728" >> /etc/sysctl.conf

   # Apply changes
   sysctl -p

ZeroMQ Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import zmq

   # Configure ZeroMQ context (if needed for advanced use cases)
   context = zmq.asyncio.Context()
   context.setsockopt(zmq.MAX_SOCKETS, 1024)
   context.setsockopt(zmq.IO_THREADS, 4)

Monitoring Configuration
------------------------

Health Checks
~~~~~~~~~~~~~

.. code-block:: python

   # health_check.py
   import asyncio
   from hydra_router.mq_client import MQClient, MessageType, ZMQMessage
   from hydra_router.router_constants import RouterConstants

   async def health_check():
       try:
           client = MQClient(
               router_address="tcp://localhost:5556",
               client_type=RouterConstants.HYDRA_CLIENT,
               client_id="health-check"
           )

           await client.connect()

           # Send test message
           message = ZMQMessage(
               message_type=MessageType.HEARTBEAT,
               timestamp=time.time(),
               client_id="health-check"
           )

           await client.send_message(message)
           await client.disconnect()

           return True

       except Exception:
           return False

Metrics Collection
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # metrics.py
   import time
   from collections import defaultdict

   class RouterMetrics:
       def __init__(self):
           self.counters = defaultdict(int)
           self.gauges = defaultdict(float)
           self.start_time = time.time()

       def increment(self, metric):
           self.counters[metric] += 1

       def set_gauge(self, metric, value):
           self.gauges[metric] = value

       def get_stats(self):
           uptime = time.time() - self.start_time
           return {
               'uptime': uptime,
               'counters': dict(self.counters),
               'gauges': dict(self.gauges)
           }

Docker Configuration
--------------------

Dockerfile
~~~~~~~~~~

.. code-block:: dockerfile

   FROM python:3.11-slim

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       build-essential \
       libzmq3-dev \
       && rm -rf /var/lib/apt/lists/*

   # Install HydraRouter
   RUN pip install hydra-router

   # Create non-root user
   RUN useradd -m -u 1000 hydra
   USER hydra

   # Expose port
   EXPOSE 5556

   # Start router
   CMD ["hydra-router", "start", "--address", "0.0.0.0", "--port", "5556"]

Docker Compose
~~~~~~~~~~~~~~

.. code-block:: yaml

   # docker-compose.yml
   version: '3.8'

   services:
     hydra-router:
       image: hydra-router:latest
       ports:
         - "5556:5556"
       environment:
         - HYDRA_ROUTER_LOG_LEVEL=INFO
       volumes:
         - ./logs:/var/log
       restart: unless-stopped

     hydra-client:
       image: hydra-router:latest
       depends_on:
         - hydra-router
       command: ["hydra-client-simple", "--router-address", "tcp://hydra-router:5556"]

Kubernetes Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # k8s-deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: hydra-router
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: hydra-router
     template:
       metadata:
         labels:
           app: hydra-router
       spec:
         containers:
         - name: hydra-router
           image: hydra-router:latest
           ports:
           - containerPort: 5556
           env:
           - name: HYDRA_ROUTER_ADDRESS
             value: "0.0.0.0"
           - name: HYDRA_ROUTER_PORT
             value: "5556"
           resources:
             requests:
               memory: "128Mi"
               cpu: "100m"
             limits:
               memory: "512Mi"
               cpu: "500m"

   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: hydra-router-service
   spec:
     selector:
       app: hydra-router
     ports:
     - protocol: TCP
       port: 5556
       targetPort: 5556
     type: LoadBalancer

This configuration guide provides comprehensive options for deploying HydraRouter in various environments, from development to production.
