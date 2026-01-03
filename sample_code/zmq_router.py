"""
ZMQ Router RPC Server Implementation.

This module provides a simple RPC server using ZeroMQ ROUTER socket pattern.
It can handle multiple clients and supports basic RPC methods like add and echo.
"""

import json
from typing import Any

import zmq


def process_rpc(method_name: str, *args: Any) -> Any:
    """Simple function to simulate RPC calls."""
    if method_name == "add":
        return sum(args)
    elif method_name == "echo":
        return args[0]
    else:
        return f"Unknown method: {method_name}"


context = zmq.Context()
server = context.socket(zmq.ROUTER)
server.bind("tcp://*:5559")
print("RPC Router Server started on port 5559...")

while True:
    try:
        # Receive all message parts: [client_identity, empty_frame, request_body]
        frames = server.recv_multipart()
        if not frames:
            continue

        identity = frames[0]
        # frames[1] is the empty delimiter frame
        request_data = frames[2]

        # Deserialize the request
        request = json.loads(request_data.decode("utf-8"))
        method = request["method"]
        params = request["params"]

        print(f"Received request from {identity}: {method}{tuple(params)}")

        # Process the request
        result = process_rpc(method, *params)

        # Serialize the response
        response_data = json.dumps({"result": result}).encode("utf-8")

        # Send multi-part reply: [client_identity, empty_frame, response_body]
        server.send_multipart([identity, b"", response_data])

    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"An error occurred: {e}")
        # In a real system, you might send an error response to the client

server.close()
context.term()
