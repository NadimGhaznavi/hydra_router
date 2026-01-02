Deployment Guide
===============

This guide covers deployment scenarios and operational considerations for HydraRouter in production environments.

Installation Methods
-------------------

PyPI Installation
~~~~~~~~~~~~~~~~

The recommended way to install HydraRouter is via PyPI:

.. code-block:: bash

    pip install hydra-router

This installs the ``hydra-router`` command-line tool and all Python dependencies.

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~

For development or customization:

.. code-block:: bash

    git clone https://github.com/your-org/hydra-router.git
    cd hydra-router
    pip install -e .

Docker Deployment
~~~~~~~~~~~~~~~~

Create a Dockerfile for containerized deployment:

.. code-block:: dockerfile

    FROM python:3.11-slim

    RUN pip install hydra-router

    EXPOSE 5556

    CMD ["hydra-router", "start", "--address", "0.0.0.0", "--port", "5556"]

Build and run:

.. code-block:: bash

    docker build -t hydra-router .
    docker run -p 5556:5556 hydra-router

Deployment Scenarios
-------------------

Single Node Deployment
~~~~~~~~~~~~~~~~~~~~~~

For simple applications, deploy HydraRouter on a single node:

.. code-block:: bash

    # Start the router
    hydra-router start --address 0.0.0.0 --port 5556 --log-level INFO

    # In separate terminals, start your applications
    python your_server.py
    python your_client.py

Multi-Node Deployment
~~~~~~~~~~~~~~~~~~~~

For distributed applications, deploy HydraRouter on a dedicated node:

**Router Node:**

.. code-block:: bash

    # On router.example.com
    hydra-router start --address 0.0.0.0 --port 5556

**Application Nodes:**

.. code-block:: python

    # Configure clients to connect to router node
    client = MQClient(
        client_type="your_client",
        router_address="tcp://router.example.com:5556"
    )

Load Balancer Integration
~~~~~~~~~~~~~~~~~~~~~~~~

When using load balancers, ensure TCP load balancing is configured:

**HAProxy Configuration:**

.. code-block:: text

    backend hydra_router
        mode tcp
        balance roundrobin
        server router1 router1.example.com:5556 check
        server router2 router2.example.com:5556 check

**NGINX Stream Configuration:**

.. code-block:: nginx

    stream {
        upstream hydra_router {
            server router1.example.com:5556;
            server router2.example.com:5556;
        }

        server {
            listen 5556;
            proxy_pass hydra_router;
        }
    }

Cloud Deployment
---------------

AWS Deployment
~~~~~~~~~~~~~

**EC2 Instance:**

1. Launch an EC2 instance with appropriate security groups
2. Install HydraRouter via pip
3. Configure security group to allow inbound traffic on port 5556

.. code-block:: bash

    # Install on EC2
    sudo yum update -y
    sudo yum install python3-pip -y
    pip3 install hydra-router

    # Start router
    hydra-router start --address 0.0.0.0 --port 5556

**ECS Deployment:**

.. code-block:: json

    {
        "family": "hydra-router",
        "containerDefinitions": [
            {
                "name": "hydra-router",
                "image": "your-registry/hydra-router:latest",
                "portMappings": [
                    {
                        "containerPort": 5556,
                        "protocol": "tcp"
                    }
                ],
                "command": [
                    "hydra-router", "start",
                    "--address", "0.0.0.0",
                    "--port", "5556"
                ]
            }
        ]
    }

Kubernetes Deployment
~~~~~~~~~~~~~~~~~~~~

**Deployment YAML:**

.. code-block:: yaml

    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: hydra-router
    spec:
      replicas: 1
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
            command: ["hydra-router", "start", "--address", "0.0.0.0", "--port", "5556"]

**Service YAML:**

.. code-block:: yaml

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

Configuration Management
-----------------------

Environment Variables
~~~~~~~~~~~~~~~~~~~

HydraRouter supports configuration via environment variables:

.. code-block:: bash

    export HYDRA_ROUTER_ADDRESS=0.0.0.0
    export HYDRA_ROUTER_PORT=5556
    export HYDRA_ROUTER_LOG_LEVEL=INFO

    hydra-router start

Configuration Files
~~~~~~~~~~~~~~~~~~

Create a configuration file for complex deployments:

.. code-block:: yaml

    # hydra-router.yaml
    router:
      address: "0.0.0.0"
      port: 5556
      log_level: "INFO"
      heartbeat_interval: 30
      client_timeout: 60

    logging:
      format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
      file: "/var/log/hydra-router.log"

Use with:

.. code-block:: bash

    hydra-router start --config hydra-router.yaml

Monitoring and Observability
---------------------------

Health Checks
~~~~~~~~~~~~

Implement health checks for deployment monitoring:

.. code-block:: python

    import zmq
    import json

    def health_check(router_address="tcp://localhost:5556"):
        """Simple health check for HydraRouter"""
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.LINGER, 1000)

        try:
            socket.connect(router_address)
            # Send a simple ping message
            socket.send_json({"type": "ping"})

            # Wait for response with timeout
            if socket.poll(5000):  # 5 second timeout
                response = socket.recv_json()
                return response.get("status") == "ok"
            return False
        except Exception:
            return False
        finally:
            socket.close()
            context.term()

Logging Configuration
~~~~~~~~~~~~~~~~~~~

Configure structured logging for production:

.. code-block:: python

    import logging
    import json

    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                'timestamp': self.formatTime(record),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            return json.dumps(log_entry)

Metrics Collection
~~~~~~~~~~~~~~~~

Monitor key metrics in production:

- **Connection Count**: Number of active client connections
- **Message Throughput**: Messages per second processed
- **Error Rate**: Failed message routing attempts
- **Response Time**: Average message processing time
- **Memory Usage**: Router process memory consumption

Security Considerations
----------------------

Network Security
~~~~~~~~~~~~~~~

- Use firewalls to restrict access to router ports
- Consider VPN or private networks for sensitive deployments
- Implement network segmentation between client types

Authentication
~~~~~~~~~~~~~

While HydraRouter doesn't include built-in authentication, implement it at the application level:

.. code-block:: python

    class AuthenticatedMQClient(MQClient):
        def __init__(self, client_type, router_address, auth_token):
            super().__init__(client_type, router_address)
            self.auth_token = auth_token

        def send_message(self, message):
            # Add authentication to all messages
            message["auth_token"] = self.auth_token
            return super().send_message(message)

Encryption
~~~~~~~~~

For sensitive data, implement message-level encryption:

.. code-block:: python

    import cryptography.fernet

    class EncryptedMQClient(MQClient):
        def __init__(self, client_type, router_address, encryption_key):
            super().__init__(client_type, router_address)
            self.cipher = Fernet(encryption_key)

        def send_message(self, message):
            # Encrypt message payload
            if "data" in message:
                message["data"] = self.cipher.encrypt(
                    json.dumps(message["data"]).encode()
                ).decode()
            return super().send_message(message)

Performance Tuning
------------------

Router Configuration
~~~~~~~~~~~~~~~~~~~

Optimize router performance for your use case:

.. code-block:: python

    # High-throughput configuration
    router = HydraRouter(
        address="0.0.0.0",
        port=5556,
        heartbeat_interval=60,  # Longer intervals for high throughput
        client_timeout=120,     # Allow longer client timeouts
        max_clients=1000        # Support more concurrent clients
    )

System Tuning
~~~~~~~~~~~~

**Linux System Limits:**

.. code-block:: bash

    # Increase file descriptor limits
    echo "* soft nofile 65536" >> /etc/security/limits.conf
    echo "* hard nofile 65536" >> /etc/security/limits.conf

    # Increase network buffer sizes
    echo "net.core.rmem_max = 16777216" >> /etc/sysctl.conf
    echo "net.core.wmem_max = 16777216" >> /etc/sysctl.conf

**ZeroMQ Tuning:**

.. code-block:: python

    # Optimize ZeroMQ socket options
    socket.setsockopt(zmq.SNDHWM, 10000)  # Send high water mark
    socket.setsockopt(zmq.RCVHWM, 10000)  # Receive high water mark
    socket.setsockopt(zmq.LINGER, 1000)   # Linger time on close

Backup and Recovery
------------------

State Management
~~~~~~~~~~~~~~~

HydraRouter is stateless by design, but consider backing up:

- Configuration files
- Application logs
- Client connection patterns (for capacity planning)

Disaster Recovery
~~~~~~~~~~~~~~~

**Router Failure Recovery:**

1. Deploy multiple router instances behind a load balancer
2. Implement client reconnection logic with exponential backoff
3. Monitor router health and automatically restart failed instances

**Data Recovery:**

Since HydraRouter doesn't persist messages, implement application-level message persistence if needed:

.. code-block:: python

    class PersistentMQClient(MQClient):
        def __init__(self, client_type, router_address, backup_store):
            super().__init__(client_type, router_address)
            self.backup_store = backup_store

        def send_message(self, message):
            # Backup message before sending
            self.backup_store.store(message)
            try:
                result = super().send_message(message)
                self.backup_store.mark_sent(message)
                return result
            except Exception:
                # Message will remain in backup for retry
                raise

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

**Connection Refused:**

.. code-block:: bash

    # Check if router is running
    netstat -tlnp | grep 5556

    # Check firewall rules
    iptables -L | grep 5556

**High Memory Usage:**

.. code-block:: bash

    # Monitor router process
    ps aux | grep hydra-router

    # Check for memory leaks
    valgrind --tool=memcheck hydra-router start

**Message Loss:**

- Verify client heartbeat configuration
- Check network stability between nodes
- Monitor router logs for error messages

Debug Mode
~~~~~~~~~

Enable debug logging for troubleshooting:

.. code-block:: bash

    hydra-router start --log-level DEBUG

This provides detailed information about:

- Client connections and disconnections
- Message routing decisions
- Error conditions and recovery attempts
- Performance metrics

Production Checklist
-------------------

Before deploying to production:

**Infrastructure:**

- [ ] Router deployed on appropriate hardware/instance size
- [ ] Network connectivity tested between all nodes
- [ ] Firewall rules configured correctly
- [ ] Load balancer configured (if applicable)
- [ ] SSL/TLS termination configured (if applicable)

**Configuration:**

- [ ] Router configuration optimized for expected load
- [ ] Logging configured for production environment
- [ ] Monitoring and alerting configured
- [ ] Health checks implemented
- [ ] Backup procedures documented

**Security:**

- [ ] Network access restricted appropriately
- [ ] Authentication implemented (if required)
- [ ] Encryption configured (if required)
- [ ] Security scanning completed

**Testing:**

- [ ] Load testing completed
- [ ] Failover scenarios tested
- [ ] Recovery procedures tested
- [ ] Performance benchmarks established

**Documentation:**

- [ ] Deployment procedures documented
- [ ] Troubleshooting guide available
- [ ] Contact information for support
- [ ] Rollback procedures documented

This deployment guide provides comprehensive coverage of production deployment scenarios and operational considerations for HydraRouter.
