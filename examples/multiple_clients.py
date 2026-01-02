#!/usr/bin/env python3
"""
Multiple Clients Example for HydraRouter.

This example demonstrates how multiple clients can connect to a single server
through the HydraRouter, showing the router's ability to handle concurrent
client connections and message routing.

Usage:
    1. Start the router: python -m hydra_router.cli start
    2. Run this example: python examples/multiple_clients.py
"""

import asyncio
import random
import time

from hydra_router.constants.DMsgType import DMsgType
from hydra_router.constants.DRouter import DRouter
from hydra_router.mq_client import MQClient, ZMQMessage


class MultiClientServer:
    """Server that handles requests from multiple clients."""

    def __init__(self) -> None:
        """Initialize the multi-client server."""
        self.client = MQClient(
            router_address="tcp://localhost:5556",
            client_type=DRouter.SIMPLE_SERVER,
            client_id="multi-server",
        )
        self.request_count = 0

    async def start(self) -> None:
        """Start the server."""
        try:
            await asyncio.wait_for(self.client.connect(), timeout=2.0)
            self.client.register_message_handler(
                DMsgType.SQUARE_REQUEST, self._handle_request
            )
            print("🔢 Multi-Client Server started")
        except asyncio.TimeoutError:
            print("⚠️  No router available - server simulation mode")
            raise

    async def stop(self) -> None:
        """Stop the server."""
        await self.client.disconnect()
        print(f"🛑 Server stopped (processed {self.request_count} requests)")

    def _handle_request(self, message: ZMQMessage) -> None:
        """Handle square calculation request."""
        self.request_count += 1
        data = message.data or {}
        number = data.get("number", 0)
        result = number * number
        client_id = message.client_id

        print(
            f"📥 Server: Request #{self.request_count} from {client_id}: {number}² = {result}"
        )

        # Send response
        response = ZMQMessage(
            message_type=DMsgType.SQUARE_RESPONSE,
            timestamp=time.time(),
            client_id="multi-server",
            request_id=message.request_id,
            data={
                "number": number,
                "result": result,
                "server_id": "multi-server",
                "request_number": self.request_count,
            },
        )

        asyncio.create_task(self.client.send_message(response))


class TestClient:
    """Individual test client."""

    def __init__(self, client_id: str, request_count: int = 5) -> None:
        """Initialize the test client."""
        self.client_id = client_id
        self.request_count = request_count
        self.client = MQClient(
            router_address="tcp://localhost:5556",
            client_type=DRouter.SIMPLE_CLIENT,
            client_id=client_id,
        )
        self.responses_received = 0

    async def start(self) -> None:
        """Start the client."""
        try:
            await asyncio.wait_for(self.client.connect(), timeout=2.0)
            self.client.register_message_handler(
                DMsgType.SQUARE_RESPONSE, self._handle_response
            )
            print(f"📱 Client {self.client_id} connected")
        except asyncio.TimeoutError:
            print(f"⚠️  Client {self.client_id}: No router available - simulation mode")
            raise

    async def stop(self) -> None:
        """Stop the client."""
        await self.client.disconnect()
        print(
            f"👋 Client {self.client_id} disconnected ({self.responses_received} responses)"
        )

    def _handle_response(self, message: ZMQMessage) -> None:
        """Handle square calculation response."""
        self.responses_received += 1
        data = message.data or {}
        number = data.get("number")
        result = data.get("result")
        request_number = data.get("request_number")

        print(f"📥 {self.client_id}: Response #{request_number}: {number}² = {result}")

    async def send_requests(self) -> None:
        """Send multiple square requests."""
        for i in range(self.request_count):
            # Random number between 1 and 20
            number = random.randint(1, 20)

            message = ZMQMessage(
                message_type=DMsgType.SQUARE_REQUEST,
                timestamp=time.time(),
                client_id=self.client_id,
                request_id=f"{self.client_id}-req-{i+1}",
                data={"number": number},
            )

            print(
                f"📤 {self.client_id}: Sending request {i+1}/{self.request_count}: {number}²"
            )
            await self.client.send_message(message)

            # Reduced delay for faster testing
            await asyncio.sleep(random.uniform(0.1, 0.3))


async def run_server(server: MultiClientServer) -> None:
    """Run the server task."""
    await server.start()

    # Keep server running
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        await server.stop()


async def run_client(client: TestClient) -> None:
    """Run a client task."""
    try:
        await client.start()
        await client.send_requests()
        # Reduced wait time for responses
        await asyncio.sleep(1)
    except asyncio.TimeoutError:
        print(f"⚠️  {client.client_id}: Simulating client behavior (no router)")
        # Simulate the client behavior for testing
        for i in range(client.request_count):
            number = random.randint(1, 20)
            print(
                f"📤 {client.client_id}: Would send request {i+1}/{client.request_count}: {number}²"
            )
            await asyncio.sleep(0.1)
    finally:
        if hasattr(client, "client") and client.client.connected:
            await client.stop()


async def main() -> None:
    """Main example function."""
    print("🚀 Multiple Clients Example")
    print("=" * 50)
    print("This example shows multiple clients connecting to one server.")
    print("Make sure to start the router first:")
    print("  python -m hydra_router.cli start")
    print()

    # Create server
    server = MultiClientServer()

    # Create multiple clients
    clients = [
        TestClient("client-alpha", 3),
        TestClient("client-beta", 4),
        TestClient("client-gamma", 2),
        TestClient("client-delta", 5),
    ]

    print(f"Starting 1 server and {len(clients)} clients...")
    print()

    try:
        # Start server task
        server_task = asyncio.create_task(run_server(server))

        # Wait a moment for server to start
        await asyncio.sleep(1)

        # Start all client tasks
        client_tasks = [asyncio.create_task(run_client(client)) for client in clients]

        # Wait for all clients to complete
        await asyncio.gather(*client_tasks)

        # Wait a bit more for any remaining responses
        await asyncio.sleep(2)

        # Cancel server task
        server_task.cancel()

        try:
            await server_task
        except asyncio.CancelledError:
            pass

        print("\n✅ Multiple clients example completed!")

    except KeyboardInterrupt:
        print("\n🛑 Example interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
