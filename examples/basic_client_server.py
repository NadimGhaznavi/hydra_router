#!/usr/bin/env python3
"""
Basic Client-Server Example for HydraRouter.

This example demonstrates the basic usage of HydraRouter with a simple
client-server communication pattern for square calculations.

Usage:
    1. Start the router: python -m hydra_router.cli start
    2. Run this example: python examples/basic_client_server.py
"""

import asyncio
import time

from hydra_router.constants.DMsgType import MsgType
from hydra_router.mq_client import MQClient, ZMQMessage
from hydra_router.router_constants import RouterConstants


async def run_server():
    """Run a simple server that calculates squares."""
    print("🔢 Starting Simple Server...")

    server = MQClient(
        router_address="tcp://localhost:5556",
        client_type=RouterConstants.SIMPLE_SERVER,
        client_id="example-server",
    )

    # Handler for square requests
    def handle_square_request(message: ZMQMessage):
        data = message.data or {}
        number = data.get("number", 0)
        result = number * number

        print(f"📥 Server: Received request to calculate {number}² = {result}")

        # Send response
        response = ZMQMessage(
            message_type=MsgType.SQUARE_RESPONSE,
            timestamp=time.time(),
            client_id="example-server",
            request_id=message.request_id,
            data={"number": number, "result": result},
        )

        asyncio.create_task(server.send_message(response))

    try:
        await server.connect()
        server.register_message_handler(MsgType.SQUARE_REQUEST, handle_square_request)
        print("✅ Server connected and ready")

        # Keep server running
        while True:
            await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        await server.disconnect()


async def run_client():
    """Run a simple client that sends square requests."""
    print("📱 Starting Simple Client...")

    client = MQClient(
        router_address="tcp://localhost:5556",
        client_type=RouterConstants.SIMPLE_CLIENT,
        client_id="example-client",
    )

    # Handler for square responses
    def handle_square_response(message: ZMQMessage):
        data = message.data or {}
        number = data.get("number")
        result = data.get("result")
        print(f"📥 Client: Received response {number}² = {result}")

    try:
        await client.connect()
        client.register_message_handler(MsgType.SQUARE_RESPONSE, handle_square_response)
        print("✅ Client connected")

        # Send some requests
        for i in range(1, 6):
            print(f"📤 Client: Sending request to calculate {i}²")

            message = ZMQMessage(
                message_type=MsgType.SQUARE_REQUEST,
                timestamp=time.time(),
                client_id="example-client",
                request_id=f"req-{i}",
                data={"number": i},
            )

            await client.send_message(message)
            await asyncio.sleep(1)  # Wait between requests

        # Wait for responses
        await asyncio.sleep(2)

    except Exception as e:
        print(f"❌ Client error: {e}")
    finally:
        await client.disconnect()


async def main():
    """Main example function."""
    print("🚀 Basic Client-Server Example")
    print("=" * 40)
    print("This example demonstrates basic HydraRouter usage.")
    print("Make sure to start the router first:")
    print("  python -m hydra_router.cli start")
    print()

    # Run server and client concurrently
    try:
        await asyncio.gather(run_server(), run_client())
    except KeyboardInterrupt:
        print("\n🛑 Example interrupted")


if __name__ == "__main__":
    asyncio.run(main())
