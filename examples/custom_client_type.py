#!/usr/bin/env python3
"""
Custom Client Type Example for HydraRouter.

This example demonstrates how to create a custom client type that extends
the basic HydraRouter functionality with specialized behavior and message
handling patterns.

Usage:
    1. Start the router: python -m hydra_router.cli start
    2. Run this example: python examples/custom_client_type.py
"""

import asyncio
import time
from enum import Enum
from typing import Any, Dict, Optional

from hydra_router.constants.DHydraLog import DHydraLog
from hydra_router.mq_client import MessageType, MQClient, ZMQMessage
from hydra_router.util.HydraLog import HydraLog


class CustomMessageType(Enum):
    """Custom message types for specialized client."""

    MATH_OPERATION = "MATH_OPERATION"
    MATH_RESULT = "MATH_RESULT"
    STATUS_REQUEST = "STATUS_REQUEST"
    STATUS_RESPONSE = "STATUS_RESPONSE"


class MathOperation(Enum):
    """Supported mathematical operations."""

    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    POWER = "power"


class CustomMathClient:
    """Custom client that performs various mathematical operations."""

    def __init__(
        self,
        router_address: str = "tcp://localhost:5556",
        client_id: Optional[str] = None,
    ):
        """Initialize the custom math client.

        Args:
            router_address: Address of the HydraRouter
            client_id: Unique client identifier (auto-generated if None)
        """
        self.router_address = router_address
        self.client_id = client_id or f"math-client-{int(time.time())}"

        # Use a custom client type
        self.client = MQClient(
            router_address=router_address,
            client_type="MATH_CLIENT",  # Custom client type
            client_id=self.client_id,
        )

        self.running = False
        self.operation_count = 0
        self.logger = HydraLog(f"math_client_{self.client_id}", to_console=True)
        self.logger.loglevel(DHydraLog.INFO)

    async def start(self) -> None:
        """Start the custom client."""
        try:
            await self.client.connect()
            self.running = True
            self.logger.info(f"Custom math client {self.client_id} connected")
            print(f"🧮 Custom Math Client connected to {self.router_address}")
            print(f"Client ID: {self.client_id}")
            print("Client Type: MATH_CLIENT")

            # Register custom message handlers
            self.client.register_message_handler(
                MessageType.SQUARE_RESPONSE, self._handle_math_result
            )

        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            print(f"❌ Connection failed: {e}")
            raise

    async def stop(self) -> None:
        """Stop the custom client."""
        self.running = False
        if self.client.connected:
            await self.client.disconnect()
            self.logger.info(f"Custom math client {self.client_id} disconnected")
            print(
                f"👋 Math client disconnected (performed {self.operation_count} operations)"
            )

    async def perform_operation(
        self, operation: MathOperation, a: float, b: float = None
    ) -> None:
        """Perform a mathematical operation.

        Args:
            operation: Type of mathematical operation
            a: First operand
            b: Second operand (if needed)
        """
        if not self.running:
            print("❌ Client not connected")
            return

        self.operation_count += 1
        request_id = f"math-{self.operation_count}-{int(time.time() * 1000)}"

        # Prepare operation data
        operation_data = {
            "operation": operation.value,
            "operand_a": a,
            "client_type": "MATH_CLIENT",
            "operation_id": self.operation_count,
        }

        if b is not None:
            operation_data["operand_b"] = b

        try:
            # For demonstration, we'll use SQUARE_REQUEST but with custom data
            message = ZMQMessage(
                message_type=MessageType.SQUARE_REQUEST,
                timestamp=time.time(),
                client_id=self.client_id,
                request_id=request_id,
                data=operation_data,
            )

            await self.client.send_message(message)

            # Display operation
            if operation == MathOperation.POWER:
                print(f"📤 Operation #{self.operation_count}: {a} ^ {b}")
            elif operation == MathOperation.ADD:
                print(f"📤 Operation #{self.operation_count}: {a} + {b}")
            elif operation == MathOperation.SUBTRACT:
                print(f"📤 Operation #{self.operation_count}: {a} - {b}")
            elif operation == MathOperation.MULTIPLY:
                print(f"📤 Operation #{self.operation_count}: {a} × {b}")
            elif operation == MathOperation.DIVIDE:
                print(f"📤 Operation #{self.operation_count}: {a} ÷ {b}")
            else:
                print(f"📤 Operation #{self.operation_count}: {operation.value}({a})")

            self.logger.info(f"Sent {operation.value} operation: {operation_data}")

        except Exception as e:
            self.logger.error(f"Failed to send operation: {e}")
            print(f"❌ Operation failed: {e}")

    def _handle_math_result(self, message: ZMQMessage) -> None:
        """Handle mathematical operation results.

        Args:
            message: Result message from server
        """
        try:
            data = message.data or {}

            # Check if this is a response to our custom operation
            if data.get("client_type") == "MATH_CLIENT":
                operation_id = data.get("operation_id")
                result = data.get("result")
                operation = data.get("operation")

                print(f"📥 Result #{operation_id}: {operation} = {result}")
                self.logger.info(
                    f"Received result for operation {operation_id}: {result}"
                )
            else:
                # Handle standard square responses
                number = data.get("number")
                result = data.get("result")
                if number is not None and result is not None:
                    print(f"📥 Square result: {number}² = {result}")

        except Exception as e:
            self.logger.error(f"Error handling result: {e}")
            print(f"❌ Error processing result: {e}")

    async def send_status_request(self) -> None:
        """Send a custom status request to demonstrate custom message types."""
        if not self.running:
            print("❌ Client not connected")
            return

        try:
            # Send a heartbeat with custom status information
            status_message = ZMQMessage(
                message_type=MessageType.HEARTBEAT,
                timestamp=time.time(),
                client_id=self.client_id,
                data={
                    "client_type": "MATH_CLIENT",
                    "operations_performed": self.operation_count,
                    "status": "active",
                    "capabilities": [
                        "add",
                        "subtract",
                        "multiply",
                        "divide",
                        "power",
                        "square",
                    ],
                },
            )

            await self.client.send_message(status_message)
            print(f"📡 Sent status update (operations: {self.operation_count})")

        except Exception as e:
            self.logger.error(f"Failed to send status: {e}")
            print(f"❌ Status update failed: {e}")


class CustomMathServer:
    """Custom server that handles mathematical operations from custom clients."""

    def __init__(
        self,
        router_address: str = "tcp://localhost:5556",
        server_id: Optional[str] = None,
    ):
        """Initialize the custom math server.

        Args:
            router_address: Address of the HydraRouter
            server_id: Unique server identifier (auto-generated if None)
        """
        self.router_address = router_address
        self.server_id = server_id or f"math-server-{int(time.time())}"

        # Use a custom server type
        self.client = MQClient(
            router_address=router_address,
            client_type="MATH_SERVER",  # Custom server type
            client_id=self.server_id,
        )

        self.running = False
        self.operations_processed = 0
        self.logger = HydraLog(f"math_server_{self.server_id}", to_console=True)
        self.logger.loglevel(DHydraLog.INFO)

    async def start(self) -> None:
        """Start the custom server."""
        try:
            await self.client.connect()
            self.running = True
            self.logger.info(f"Custom math server {self.server_id} connected")
            print(f"🧮 Custom Math Server connected to {self.router_address}")
            print(f"Server ID: {self.server_id}")
            print("Server Type: MATH_SERVER")
            print("Ready to process mathematical operations...")

            # Register message handlers
            self.client.register_message_handler(
                MessageType.SQUARE_REQUEST, self._handle_math_operation
            )

        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            print(f"❌ Connection failed: {e}")
            raise

    async def stop(self) -> None:
        """Stop the custom server."""
        self.running = False
        if self.client.connected:
            await self.client.disconnect()
            self.logger.info(f"Custom math server {self.server_id} disconnected")
            print(
                f"👋 Math server disconnected (processed {self.operations_processed} operations)"
            )

    def _handle_math_operation(self, message: ZMQMessage) -> None:
        """Handle mathematical operation requests.

        Args:
            message: Request message from client
        """
        try:
            data = message.data or {}
            client_id = message.client_id
            request_id = message.request_id

            # Check if this is a custom math operation
            if data.get("client_type") == "MATH_CLIENT":
                self._process_custom_operation(data, client_id, request_id)
            else:
                # Handle standard square operations
                self._process_square_operation(data, client_id, request_id)

        except Exception as e:
            self.logger.error(f"Error handling operation: {e}")
            print(f"❌ Error processing operation: {e}")

    def _process_custom_operation(
        self, data: Dict[str, Any], client_id: str, request_id: str
    ) -> None:
        """Process custom mathematical operations."""
        operation = data.get("operation")
        operand_a = data.get("operand_a")
        operand_b = data.get("operand_b")
        operation_id = data.get("operation_id")

        self.operations_processed += 1

        try:
            # Perform the calculation
            if operation == "add":
                result = operand_a + operand_b
            elif operation == "subtract":
                result = operand_a - operand_b
            elif operation == "multiply":
                result = operand_a * operand_b
            elif operation == "divide":
                if operand_b == 0:
                    result = "Error: Division by zero"
                else:
                    result = operand_a / operand_b
            elif operation == "power":
                result = operand_a**operand_b
            else:
                result = f"Error: Unknown operation '{operation}'"

            print(
                f"📥 Custom Operation #{self.operations_processed}: {operation}({operand_a}, {operand_b}) = {result}"
            )

            # Send response
            response = ZMQMessage(
                message_type=MessageType.SQUARE_RESPONSE,
                timestamp=time.time(),
                client_id=self.server_id,
                request_id=request_id,
                data={
                    "client_type": "MATH_CLIENT",
                    "operation": operation,
                    "operation_id": operation_id,
                    "operand_a": operand_a,
                    "operand_b": operand_b,
                    "result": result,
                    "server_id": self.server_id,
                },
            )

            asyncio.create_task(self.client.send_message(response))
            print(f"📤 Response sent: {operation} = {result}")

        except Exception as e:
            self.logger.error(f"Error calculating {operation}: {e}")

    def _process_square_operation(
        self, data: Dict[str, Any], client_id: str, request_id: str
    ) -> None:
        """Process standard square operations."""
        number = data.get("number")

        if number is None:
            self.logger.warning(
                f"Invalid square request from {client_id}: missing number"
            )
            return

        result = number * number
        self.operations_processed += 1

        print(f"📥 Square Operation #{self.operations_processed}: {number}² = {result}")

        # Send response
        response = ZMQMessage(
            message_type=MessageType.SQUARE_RESPONSE,
            timestamp=time.time(),
            client_id=self.server_id,
            request_id=request_id,
            data={"number": number, "result": result, "server_id": self.server_id},
        )

        asyncio.create_task(self.client.send_message(response))
        print(f"📤 Response sent: {number}² = {result}")


async def run_custom_server():
    """Run the custom math server."""
    server = CustomMathServer()

    try:
        await server.start()

        # Keep server running
        while server.running:
            await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        await server.stop()


async def run_custom_client():
    """Run the custom math client with demonstration operations."""
    # Wait for server to start
    await asyncio.sleep(2)

    client = CustomMathClient()

    try:
        await client.start()

        # Demonstrate various custom operations
        operations = [
            (MathOperation.ADD, 15, 25),
            (MathOperation.SUBTRACT, 100, 37),
            (MathOperation.MULTIPLY, 7, 8),
            (MathOperation.DIVIDE, 144, 12),
            (MathOperation.POWER, 2, 8),
        ]

        print("\n🎯 Demonstrating Custom Mathematical Operations:")
        print("-" * 50)

        for operation, a, b in operations:
            await client.perform_operation(operation, a, b)
            await asyncio.sleep(1.5)

        # Send status update
        await client.send_status_request()

        # Wait for responses
        await asyncio.sleep(3)

    except Exception as e:
        print(f"❌ Client error: {e}")
    finally:
        await client.stop()


async def main():
    """Main example function."""
    print("🚀 Custom Client Type Example")
    print("=" * 50)
    print("This example demonstrates custom client and server types")
    print("with specialized mathematical operations beyond simple squares.")
    print("Make sure to start the router first:")
    print("  python -m hydra_router.cli start")
    print()

    try:
        # Run custom server and client concurrently
        server_task = asyncio.create_task(run_custom_server())
        client_task = asyncio.create_task(run_custom_client())

        # Wait for client to complete
        await client_task

        # Cancel server task
        server_task.cancel()

        try:
            await server_task
        except asyncio.CancelledError:
            pass

        print("\n✅ Custom client type example completed!")
        print("This demonstrated:")
        print("  • Custom client and server types (MATH_CLIENT, MATH_SERVER)")
        print("  • Extended message handling beyond basic square calculations")
        print("  • Custom data structures and operation types")
        print("  • Specialized client-server communication patterns")

    except KeyboardInterrupt:
        print("\n🛑 Example interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
