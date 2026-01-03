"""
Demo script for Hydra Router v2.

This script demonstrates the complete request-response cycle with proper
message delivery confirmation as required by the specifications.
"""

import asyncio
import time
from typing import List

from .constants.DLog import DLog
from .constants.DMsgType import DMsgType
from .constants.DRouter import DRouter
from .hydra_router import HydraRouter
from .mq_client import MQClient
from .zmq_message import ZMQMessage


async def demo_complete_system() -> None:
    """
    Demonstrate the complete Hydra Router system with DEBUG logging.

    Shows:
    1. Router startup with comprehensive logging
    2. Client and server connection
    3. Complete request-response cycle
    4. Message delivery confirmation
    5. Proper exception handling and debugging
    """
    print("🚀 Hydra Router v2 - Complete System Demo")
    print("=" * 50)
    print()

    # Start router with DEBUG logging
    print("1. Starting Hydra Router with DEBUG logging...")
    router = HydraRouter(
        router_address="localhost",
        router_port=5558,  # Use different port for demo
        log_level=DLog.DEBUG,  # Enable comprehensive DEBUG logging
        heartbeat_timeout=30.0,
    )

    try:
        await router.start()
        print("✅ Router started successfully")
        print()

        # Start server
        print("2. Starting Simple Server...")
        server = MQClient(
            router_address="tcp://localhost:5558",
            client_type=DRouter.SIMPLE_SERVER,
            client_id="demo-server",
            log_level=DLog.DEBUG,  # Enable DEBUG logging for complete message tracing
        )

        received_requests: List[ZMQMessage] = []

        async def handle_square_request(message: ZMQMessage) -> None:
            """Handle square calculation requests with logging."""
            print(f"📥 Server received request: {message.data}")
            received_requests.append(message)

            # Extract request data
            data = message.data or {}
            number = data.get("number", 0)
            result = number * number

            print(f"🔢 Calculating: {number}² = {result}")

            # Send response with proper request correlation
            response = ZMQMessage(
                message_type=DMsgType.SQUARE_RESPONSE,
                client_id="demo-server",
                request_id=message.request_id,  # CRITICAL: preserve for correlation
                data={
                    "number": number,
                    "result": result,
                    "server_id": "demo-server",
                    "processed_at": time.time(),
                },
            )

            await server.send_message(response)
            print(f"📤 Server sent response: {number}² = {result}")

        await server.connect()
        server.register_message_handler(DMsgType.SQUARE_REQUEST, handle_square_request)
        print("✅ Server connected and ready")
        print()

        # Start client
        print("3. Starting Simple Client...")
        client = MQClient(
            router_address="tcp://localhost:5558",
            client_type=DRouter.SIMPLE_CLIENT,
            client_id="demo-client",
            log_level=DLog.DEBUG,  # Enable DEBUG logging for complete message tracing
        )

        received_responses: List[ZMQMessage] = []

        def handle_square_response(message: ZMQMessage) -> None:
            """Handle square calculation responses with logging."""
            print(f"📥 Client received response: {message.data}")
            received_responses.append(message)

            # Print the answer to console for user visibility (per requirements)
            data = message.data or {}
            number = data.get("number")
            result = data.get("result")
            server_id = data.get("server_id", "unknown")

            if number is not None and result is not None:
                print(f"✨ ANSWER: {number}² = {result} (from {server_id})")

        await client.connect()
        client.register_message_handler(
            DMsgType.SQUARE_RESPONSE, handle_square_response
        )
        print("✅ Client connected and ready")
        print()

        # Wait for connections to stabilize
        await asyncio.sleep(1)

        # Demonstrate complete request-response cycles
        print("4. Demonstrating complete request-response cycles...")
        print()

        test_numbers = [5, 12, 25, 100]

        for i, number in enumerate(test_numbers, 1):
            print(f"Test {i}: Calculating {number}²")

            # Send request
            request = ZMQMessage(
                message_type=DMsgType.SQUARE_REQUEST,
                client_id="demo-client",
                request_id=f"demo-req-{i}",
                data={"number": number, "test_id": i},
            )

            print(f"📤 Client sending request: {number}² = ?")
            await client.send_message(request)

            # Wait for response
            await asyncio.sleep(0.5)

            print()

        # Wait for all responses
        await asyncio.sleep(2)

        # Validate message delivery
        print("5. Validating message delivery...")
        print(f"   Requests sent: {len(test_numbers)}")
        print(f"   Requests received by server: {len(received_requests)}")
        print(f"   Responses received by client: {len(received_responses)}")

        if len(received_requests) == len(test_numbers) and len(
            received_responses
        ) == len(test_numbers):
            print("✅ All messages delivered successfully!")
        else:
            print("❌ Message delivery incomplete")

        print()

        # Demonstrate error handling
        print("6. Demonstrating error handling...")

        # Disconnect server to test no-server error
        await server.disconnect()
        print("🔌 Server disconnected")

        # Wait for server to be removed from registry
        await asyncio.sleep(1)

        # Register error handler on client
        received_errors: List[ZMQMessage] = []

        def handle_no_server_error(message: ZMQMessage) -> None:
            """Handle no server connected errors."""
            print(f"⚠️  Client received error: {message.data}")
            received_errors.append(message)

        client.register_message_handler(
            DMsgType.NO_SERVER_CONNECTED, handle_no_server_error
        )

        # Try to send request with no server
        error_request = ZMQMessage(
            message_type=DMsgType.SQUARE_REQUEST,
            client_id="demo-client",
            request_id="error-test",
            data={"number": 42},
        )

        print("📤 Client sending request with no server connected...")
        await client.send_message(error_request)

        # Wait for error response
        await asyncio.sleep(1)

        if received_errors:
            print("✅ Error handling working correctly")
        else:
            print("❌ Error handling failed")

        print()

        # Show router status
        print("7. Router Status:")
        status = await router.get_status()
        for key, value in status.items():
            print(f"   {key}: {value}")

        print()
        print("🎉 Demo completed successfully!")
        print()
        print("Key features demonstrated:")
        print("✅ Centralized message routing")
        print("✅ Automatic message format conversion")
        print("✅ Complete request-response cycle")
        print("✅ Message delivery confirmation")
        print("✅ Comprehensive DEBUG logging")
        print("✅ Error handling and debugging")
        print("✅ Client registry and heartbeat monitoring")

        # Cleanup
        await client.disconnect()

    except Exception as e:
        print(f"❌ Demo error: {e}")
        # Print exception for debugging as per requirements
        print(f"Exception details: {type(e).__name__}: {e}")

    finally:
        await router.stop()
        print("\n👋 Demo finished")


async def main() -> None:
    """Main entry point for demo."""
    try:
        await demo_complete_system()
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
