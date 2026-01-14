Target Architecture
===================

Sample Code
-----------

```
# Client side (DEALER):
mq = HydraMQ(id="client-123")
msg = HydraMsg(sender="client-123", target="service-X", method="ping", payload={...})
await mq.send(msg)
response = await mq.recv()  # Returns HydraMsg

# Router side (ROUTER):
router_socket = ctx.socket(zmq.ROUTER)
router_socket.bind("tcp://*:5757")

while True:
    # Receive: [sender_id, b"", message_data]
    frames = await router_socket.recv_multipart()
    sender_id = frames[0]
    msg = HydraMsg.from_json(frames[2].decode())
    
    # Route to target
    target_id = msg.target.encode()
    await router_socket.send_multipart([
        target_id,  # Destination
        b"",
        frames[2]  # Forward message
    ])

# Service side (DEALER):
mq = HydraMQ(id="service-X")
request = await mq.recv()  # Returns HydraMsg
response = HydraMsg(sender="service-X", target=request.sender, method="pong", payload={...})
await mq.send(response)
```