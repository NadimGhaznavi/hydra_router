#!/usr/bin/env python3
"""
Debug script to test basic router-client communication.
"""

import asyncio
import time

from hydra_router.constants.DMsgType import DMsgType
from hydra_router.constants.DRouter import DRouter
from hydra_router.mq_client import MQClient, ZMQMessage
from hydra_router.router import HydraRouter


async def debug_communication():
    """Debug basic communication."""
    print("🔍 Starting debug session...")

    # Start router
    router = HydraRouter(
        router_address="127.0.0.1",
        router_port=5560,
        client_timeout=10.0,
    )

    try:
        await router.start()
        print("✅ Router started")

        # Create client
        client = MQClient(
            router_address="tcp://127.0.0.1:5560",
            client_type=DRouter.SIMPLE_CLIENT,
            client_id="debug-client",
        )

        try:
            print("🔌 Connecting client...")
            await client.connect()
            print("✅ Client connected")

            # Wait a bit
            await asyncio.sleep(2.0)

            # Check router status
            status = await router.get_status()
            print(f"📊 Router status: {status['client_count']} clients")
            print(f"📋 Clients: {list(status['clients'].keys())}")

            # Try sending a manual heartbeat
            print("💓 Sending manual heartbeat...")
            heartbeat = ZMQMessage(
                message_type=DMsgType.HEARTBEAT,
                timestamp=time.time(),
                client_id="debug-client",
            )

            await client.send_message(heartbeat)
            print("✅ Manual heartbeat sent")

            # Wait and check again
            await asyncio.sleep(1.0)
            status = await router.get_status()
            print(f"📊 Router status after heartbeat: {status['client_count']} clients")

        finally:
            await client.disconnect()
            print("🔌 Client disconnected")

    finally:
        await router.shutdown()
        print("🛑 Router shutdown")


if __name__ == "__main__":
    asyncio.run(debug_communication())
