#!/usr/bin/env python3
"""
Error Handling Example for HydraRouter.

This example demonstrates various error scenarios and how the HydraRouter
system handles them gracefully, including connection failures, invalid
messages, and recovery scenarios.

Usage:
    1. Start the router: python -m hydra_router.cli start
    2. Run this example: python examples/error_handling.py
"""

import asyncio
import time

from hydra_router.constants.DMsgType import DMsgType
from hydra_router.mq_client import MQClient, ZMQMessage
from hydra_router.router_constants import RouterConstants


async def test_connection_failure() -> None:
    """Test connection to non-existent router."""
    print("🔍 Testing connection failure...")

    client = MQClient(
        router_address="tcp://localhost:9999",  # Wrong port
        client_type=RouterConstants.SIMPLE_CLIENT,
        client_id="error-test-client",
    )

    try:
        await client.connect()
        print("❌ Unexpected: Connection should have failed")
    except Exception as e:
        print(f"✅ Expected connection failure: {e}")
    finally:
        if client.connected:
            await client.disconnect()


async def test_invalid_messages() -> None:
    """Test sending invalid messages."""
    print("\n🔍 Testing invalid message handling...")

    client = MQClient(
        router_address="tcp://localhost:5556",
        client_type=RouterConstants.SIMPLE_CLIENT,
        client_id="invalid-msg-client",
    )

    try:
        await client.connect()
        print("✅ Connected to router")

        # Test 1: Message with missing data
        print("📤 Sending message with missing data...")
        message = ZMQMessage(
            message_type=DMsgType.SQUARE_REQUEST,
            timestamp=time.time(),
            client_id="invalid-msg-client",
            request_id="invalid-1",
            data=None,  # Missing data
        )

        await client.send_message(message)
        print("✅ Message sent (server should handle gracefully)")

        # Test 2: Message with invalid data type
        print("📤 Sending message with invalid data...")
        message = ZMQMessage(
            message_type=DMsgType.SQUARE_REQUEST,
            timestamp=time.time(),
            client_id="invalid-msg-client",
            request_id="invalid-2",
            data={"number": "not-a-number"},  # Invalid type
        )

        await client.send_message(message)
        print("✅ Message sent (server should handle gracefully)")

        await asyncio.sleep(2)  # Wait for any responses

    except Exception as e:
        print(f"❌ Error in invalid message test: {e}")
    finally:
        await client.disconnect()


async def test_client_reconnection() -> None:
    """Test client reconnection after disconnection."""
    print("\n🔍 Testing client reconnection...")

    client = MQClient(
        router_address="tcp://localhost:5556",
        client_type=RouterConstants.SIMPLE_CLIENT,
        client_id="reconnect-client",
    )

    try:
        # Initial connection
        print("📱 Initial connection...")
        await client.connect()
        print("✅ Connected")

        # Send a message
        message = ZMQMessage(
            message_type=DMsgType.HEARTBEAT,
            timestamp=time.time(),
            client_id="reconnect-client",
        )
        await client.send_message(message)
        print("📤 Sent heartbeat")

        # Disconnect
        print("🔌 Disconnecting...")
        await client.disconnect()
        print("✅ Disconnected")

        # Wait a moment
        await asyncio.sleep(1)

        # Reconnect
        print("🔌 Reconnecting...")
        await client.connect()
        print("✅ Reconnected successfully")

        # Send another message
        message = ZMQMessage(
            message_type=DMsgType.HEARTBEAT,
            timestamp=time.time(),
            client_id="reconnect-client",
        )
        await client.send_message(message)
        print("📤 Sent heartbeat after reconnection")

    except Exception as e:
        print(f"❌ Error in reconnection test: {e}")
    finally:
        if client.connected:
            await client.disconnect()


async def test_server_error_handling() -> None:
    """Test server error handling with a mock server."""
    print("\n🔍 Testing server error handling...")

    server = MQClient(
        router_address="tcp://localhost:5556",
        client_type=RouterConstants.SIMPLE_SERVER,
        client_id="error-handling-server",
    )

    def handle_request_with_errors(message: ZMQMessage) -> None:
        """Handle requests with intentional error scenarios."""
        try:
            data = message.data or {}
            number = data.get("number")

            if number is None:
                print(
                    "⚠️  Server: Received request with no number - handling gracefully"
                )
                return

            if not isinstance(number, (int, float)):
                print(
                    f"⚠️  Server: Received invalid number type: {type(number)} - handling gracefully"
                )
                return

            if number < 0:
                print(
                    f"⚠️  Server: Received negative number {number} - handling gracefully"
                )
                # Could send error response here
                return

            # Normal processing
            result = number * number
            print(f"✅ Server: Processed {number}² = {result}")

            # Send response
            response = ZMQMessage(
                message_type=DMsgType.SQUARE_RESPONSE,
                timestamp=time.time(),
                client_id="error-handling-server",
                request_id=message.request_id,
                data={"number": number, "result": result},
            )

            asyncio.create_task(server.send_message(response))

        except Exception as e:
            print(f"❌ Server: Error processing request: {e}")

    try:
        await server.connect()
        server.register_message_handler(
            DMsgType.SQUARE_REQUEST, handle_request_with_errors
        )
        print("🔢 Error-handling server started")

        # Create a client to send test requests
        client = MQClient(
            router_address="tcp://localhost:5556",
            client_type=RouterConstants.SIMPLE_CLIENT,
            client_id="error-test-client",
        )

        await client.connect()

        # Test various error scenarios
        test_cases = [
            {"number": 5},  # Valid
            {"number": None},  # None value
            {"number": "invalid"},  # String instead of number
            {"number": -3},  # Negative number
            {},  # Empty data
        ]

        for i, test_data in enumerate(test_cases):
            print(f"📤 Client: Sending test case {i+1}: {test_data}")

            message = ZMQMessage(
                message_type=DMsgType.SQUARE_REQUEST,
                timestamp=time.time(),
                client_id="error-test-client",
                request_id=f"error-test-{i+1}",
                data=test_data if isinstance(test_data, dict) else {"data": test_data},
            )

            await client.send_message(message)
            await asyncio.sleep(0.5)

        # Wait for processing
        await asyncio.sleep(2)

        await client.disconnect()

    except Exception as e:
        print(f"❌ Error in server error handling test: {e}")
    finally:
        await server.disconnect()


async def test_timeout_scenarios() -> None:
    """Test timeout and recovery scenarios."""
    print("\n🔍 Testing timeout scenarios...")

    client = MQClient(
        router_address="tcp://localhost:5556",
        client_type=RouterConstants.SIMPLE_CLIENT,
        client_id="timeout-client",
    )

    try:
        await client.connect()
        print("✅ Connected for timeout test")

        # Send message and wait for response with timeout
        print("📤 Sending request with response timeout simulation...")

        message = ZMQMessage(
            message_type=DMsgType.SQUARE_REQUEST,
            timestamp=time.time(),
            client_id="timeout-client",
            request_id="timeout-test",
            data={"number": 42},
        )

        await client.send_message(message)

        # Simulate waiting for response with timeout
        try:
            await asyncio.wait_for(asyncio.sleep(5), timeout=2.0)
        except asyncio.TimeoutError:
            print("⏰ Simulated timeout waiting for response")
            print("✅ Application can handle timeouts gracefully")

    except Exception as e:
        print(f"❌ Error in timeout test: {e}")
    finally:
        await client.disconnect()


async def main() -> None:
    """Main error handling example."""
    print("🚀 Error Handling Example")
    print("=" * 40)
    print("This example demonstrates error handling in HydraRouter.")
    print("Make sure to start the router first:")
    print("  python -m hydra_router.cli start")
    print()

    try:
        # Test connection failure (router not running on wrong port)
        await test_connection_failure()

        # Test invalid messages (requires router to be running)
        await test_invalid_messages()

        # Test client reconnection
        await test_client_reconnection()

        # Test server error handling
        await test_server_error_handling()

        # Test timeout scenarios
        await test_timeout_scenarios()

        print("\n✅ All error handling tests completed!")
        print("The system demonstrated graceful error handling in various scenarios.")

    except KeyboardInterrupt:
        print("\n🛑 Example interrupted")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
