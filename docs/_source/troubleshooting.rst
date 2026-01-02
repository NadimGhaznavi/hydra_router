Troubleshooting
===============

This guide helps you diagnose and resolve common issues with HydraRouter.

Common Issues
-------------

Connection Problems
~~~~~~~~~~~~~~~~~~~

**Problem**: Client cannot connect to router

**Symptoms**:
- Connection timeout errors
- "Connection refused" messages
- Client hangs during connection

**Solutions**:

1. **Check if router is running**:

   .. code-block:: bash

      # Check if router process is running
      ps aux | grep hydra-router

      # Check if port is listening
      netstat -ln | grep 5556

2. **Verify router address and port**:

   .. code-block:: python

      # Make sure client uses correct address
      client = MQClient(
          router_address="tcp://localhost:5556",  # Check this matches router
          client_type=RouterConstants.HYDRA_CLIENT,
          client_id="test-client"
      )

3. **Check firewall settings**:

   .. code-block:: bash

      # On Linux, check iptables
      sudo iptables -L

      # On macOS, check pfctl
      sudo pfctl -s rules

4. **Test network connectivity**:

   .. code-block:: bash

      # Test if port is reachable
      telnet localhost 5556

      # Or use nc (netcat)
      nc -zv localhost 5556

Message Validation Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Messages are rejected with validation errors

**Symptoms**:
- "Invalid message format" errors
- Messages not being processed
- Validation error logs

**Solutions**:

1. **Check message format**:

   .. code-block:: python

      # Ensure message follows RouterConstants format
      message = {
          RouterConstants.SENDER: "client-id",      # Required
          RouterConstants.ELEM: "SQUARE_REQUEST",   # Required
          RouterConstants.TIMESTAMP: time.time(),   # Required
          RouterConstants.DATA: {"number": 5}       # Optional
      }

2. **Validate message before sending**:

   .. code-block:: python

      from hydra_router.validation import MessageValidator

      validator = MessageValidator()
      is_valid, error = validator.validate_router_message(message)
      if not is_valid:
          print(f"Validation error: {error}")

3. **Check client type**:

   .. code-block:: python

      # Ensure client type is valid
      valid_types = RouterConstants.VALID_CLIENT_TYPES
      if client_type not in valid_types:
          print(f"Invalid client type: {client_type}")

Performance Issues
~~~~~~~~~~~~~~~~~~

**Problem**: Slow message processing or high latency

**Symptoms**:
- Messages take long time to process
- High CPU usage
- Memory usage growing over time

**Solutions**:

1. **Check system resources**:

   .. code-block:: bash

      # Monitor CPU and memory usage
      top -p $(pgrep hydra-router)

      # Check network usage
      iftop

2. **Enable debug logging**:

   .. code-block:: bash

      # Start router with debug logging
      hydra-router start --log-level DEBUG

3. **Monitor client connections**:

   .. code-block:: python

      # Check number of connected clients
      registry_request = ZMQMessage(
          message_type=MessageType.CLIENT_REGISTRY_REQUEST,
          timestamp=time.time(),
          client_id="monitor"
      )

4. **Optimize message size**:

   .. code-block:: python

      # Keep message data small
      data = {"number": 5}  # Good
      # Avoid large data payloads in messages

Memory Leaks
~~~~~~~~~~~~

**Problem**: Router memory usage grows over time

**Symptoms**:
- Increasing memory usage
- System becomes slow
- Out of memory errors

**Solutions**:

1. **Check for inactive clients**:

   .. code-block:: python

      # Router automatically prunes inactive clients
      # Check pruning interval and timeout settings
      pruned = router.client_registry.prune_inactive_clients(timeout=300)
      print(f"Pruned {len(pruned)} inactive clients")

2. **Monitor client lifecycle**:

   .. code-block:: python

      # Ensure clients properly disconnect
      try:
          await client.connect()
          # Do work
      finally:
          await client.disconnect()  # Always disconnect

3. **Check for message handler leaks**:

   .. code-block:: python

      # Unregister handlers when done
      client.register_message_handler(MessageType.SQUARE_RESPONSE, handler)
      # Later...
      client.unregister_message_handler(MessageType.SQUARE_RESPONSE)

Debugging Techniques
--------------------

Enable Detailed Logging
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from hydra_router.util.HydraLog import HydraLog
   from hydra_router.constants.DHydraLog import DHydraLog

   # Enable debug logging
   logger = HydraLog("debug_app", to_console=True)
   logger.loglevel(DHydraLog.DEBUG)

   # Use the logger for debugging
   logger.debug("Debug information")
   logger.info("Application status")

Message Tracing
~~~~~~~~~~~~~~~

.. code-block:: python

   # Add request IDs to trace messages
   message = ZMQMessage(
       message_type=MessageType.SQUARE_REQUEST,
       timestamp=time.time(),
       client_id="debug-client",
       request_id=f"trace-{uuid.uuid4()}",  # Unique ID for tracing
       data={"number": 5}
   )

Network Debugging
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Monitor network traffic
   sudo tcpdump -i lo port 5556

   # Check ZeroMQ socket states
   ss -tuln | grep 5556

Client Registry Inspection
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Request client registry information
   async def inspect_registry(client):
       request = ZMQMessage(
           message_type=MessageType.CLIENT_REGISTRY_REQUEST,
           timestamp=time.time(),
           client_id="inspector"
       )

       await client.send_message(request)
       # Check response for connected clients

Error Messages Reference
------------------------

Common Error Messages and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**"Connection refused"**
   - Router is not running
   - Wrong address or port
   - Firewall blocking connection

**"Message validation failed"**
   - Invalid message format
   - Missing required fields
   - Invalid client type

**"Client not registered"**
   - Client disconnected unexpectedly
   - Heartbeat timeout
   - Router restarted

**"Unknown message type"**
   - Unsupported message type
   - Typo in message type string
   - Version mismatch

**"Socket operation on non-socket"**
   - ZeroMQ context issues
   - Improper socket cleanup
   - Threading issues

Performance Tuning
-------------------

Router Optimization
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Adjust client pruning interval
   router = HydraRouter(address="0.0.0.0", port=5556)

   # Prune inactive clients more frequently
   async def custom_pruning():
       while router.running:
           pruned = router.client_registry.prune_inactive_clients(timeout=60)
           if pruned:
               print(f"Pruned {len(pruned)} clients")
           await asyncio.sleep(30)

Client Optimization
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Use connection pooling for multiple operations
   class ClientPool:
       def __init__(self, router_address, pool_size=5):
           self.clients = []
           for i in range(pool_size):
               client = MQClient(
                   router_address=router_address,
                   client_type=RouterConstants.HYDRA_CLIENT,
                   client_id=f"pool-client-{i}"
               )
               self.clients.append(client)

       async def get_client(self):
           # Return available client from pool
           pass

System Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Increase system limits for high-load scenarios

   # Increase file descriptor limit
   ulimit -n 65536

   # Adjust network buffer sizes
   echo 'net.core.rmem_max = 134217728' >> /etc/sysctl.conf
   echo 'net.core.wmem_max = 134217728' >> /etc/sysctl.conf

Monitoring and Alerting
-----------------------

Health Checks
~~~~~~~~~~~~~

.. code-block:: python

   async def health_check():
       """Simple health check for router availability."""
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

       except Exception as e:
           print(f"Health check failed: {e}")
           return False

Metrics Collection
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class RouterMetrics:
       def __init__(self):
           self.message_count = 0
           self.error_count = 0
           self.client_count = 0

       def record_message(self):
           self.message_count += 1

       def record_error(self):
           self.error_count += 1

       def update_client_count(self, count):
           self.client_count = count

Getting Help
------------

If you're still experiencing issues:

1. **Check the logs**: Enable debug logging to get detailed information
2. **Review examples**: Look at the examples directory for working code
3. **Check GitHub issues**: Search for similar problems in the issue tracker
4. **Create minimal reproduction**: Create a simple test case that reproduces the issue
5. **Report bugs**: Open an issue with detailed information about your environment and the problem

**When reporting issues, include**:
- HydraRouter version
- Python version
- Operating system
- Complete error messages
- Minimal code to reproduce the issue
- Log output with debug level enabled

**Useful debugging information**:

.. code-block:: bash

   # System information
   python --version
   pip show hydra-router
   uname -a

   # Network information
   netstat -tuln | grep 5556
   ss -tuln | grep 5556

   # Process information
   ps aux | grep hydra-router
