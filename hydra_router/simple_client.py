"""
SimpleClient - Example client application for the Hydra Router system.

This module provides a simple interactive client that connects to a HydraRouter
and sends square calculation requests. It demonstrates basic usage of the MQClient
library for client applications.
"""

import asyncio
import sys
import time
from typing import Optional

from .constants.DHydraLog import DHydraLog
from .constants.DMsgType import DMsgType
from .constants.DRouter import DRouter
from .mq_client import MQClient, ZMQMessage
from .util.HydraLog import HydraLog


class SimpleClient:
    """Simple interactive client for square calculation requests."""

    def __init__(
        self,
        router_address: str = "tcp://localhost:5556",
        client_id: Optional[str] = None,
    ):
        """Initialize the simple client.

        Args:
            router_address: Address of the HydraRouter
            client_id: Unique client identifier (auto-generated if None)
        """
        self.router_address = router_address
        self.client_id = client_id or f"simple-client-{int(time.time())}"
        self.client = MQClient(
            router_address=router_address,
            client_type=DRouter.SIMPLE_CLIENT,
            client_id=self.client_id,
        )
        self.running = False
        self.logger = HydraLog(f"simple_client_{self.client_id}", to_console=True)
        self.logger.loglevel(DHydraLog.INFO)

    async def start(self) -> None:
        """Start the client and connect to router."""
        try:
            await self.client.connect()
            self.running = True
            self.logger.info(
                f"Simple client {self.client_id} connected to {self.router_address}"
            )
            print(f"✅ Connected to router at {self.router_address}")
            print(f"Client ID: {self.client_id}")

            # Register response handler
            self.client.register_message_handler(
                DMsgType.SQUARE_RESPONSE, self._handle_square_response
            )

        except Exception as e:
            self.logger.error(f"Failed to connect to router: {e}")
            print(f"❌ Failed to connect to router: {e}")
            raise

    async def stop(self) -> None:
        """Stop the client and disconnect from router."""
        self.running = False
        if self.client.connected:
            await self.client.disconnect()
            self.logger.info(f"Simple client {self.client_id} disconnected")
            print("👋 Disconnected from router")

    async def send_square_request(self, number: int) -> None:
        """Send a square calculation request.

        Args:
            number: Integer to calculate square of
        """
        if not self.running:
            print("❌ Client not connected")
            return

        try:
            request_id = f"req-{int(time.time() * 1000)}"
            message = ZMQMessage(
                message_type=DMsgType.SQUARE_REQUEST,
                timestamp=time.time(),
                client_id=self.client_id,
                request_id=request_id,
                data={"number": number},
            )

            await self.client.send_message(message)
            self.logger.info(
                f"Sent square request for {number} (request_id: {request_id})"
            )
            print(f"📤 Sent request: {number}² = ?")

        except Exception as e:
            self.logger.error(f"Failed to send square request: {e}")
            print(f"❌ Failed to send request: {e}")

    def _handle_square_response(self, message: ZMQMessage) -> None:
        """Handle square calculation response.

        Args:
            message: Response message from server
        """
        try:
            data = message.data or {}
            number = data.get("number")
            result = data.get("result")

            if number is not None and result is not None:
                print(f"📥 Response: {number}² = {result}")
                self.logger.info(f"Received square response: {number}² = {result}")
            else:
                print(f"📥 Response: {data}")
                self.logger.warning(f"Unexpected response format: {data}")

        except Exception as e:
            self.logger.error(f"Error handling square response: {e}")
            print(f"❌ Error processing response: {e}")

    async def run_interactive(self) -> None:
        """Run interactive client session."""
        print("\n🔢 Simple Square Calculator Client")
        print("=" * 40)
        print("Enter integers to calculate their squares")
        print("Commands: 'quit' or 'exit' to stop, 'help' for help")
        print()

        while self.running:
            try:
                # Get user input
                user_input = input("Enter number (or command): ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    break
                elif user_input.lower() in ["help", "h"]:
                    self._show_help()
                    continue
                elif user_input == "":
                    continue

                # Try to parse as integer
                try:
                    number = int(user_input)
                    await self.send_square_request(number)
                except ValueError:
                    print(f"❌ Invalid input: '{user_input}' is not an integer")

            except KeyboardInterrupt:
                print("\n🛑 Interrupted by user")
                break
            except EOFError:
                print("\n🛑 End of input")
                break
            except Exception as e:
                self.logger.error(f"Error in interactive loop: {e}")
                print(f"❌ Error: {e}")

        await self.stop()

    def _show_help(self) -> None:
        """Show help information."""
        print("\n📖 Help:")
        print("  - Enter any integer to calculate its square")
        print("  - 'quit' or 'exit' - Exit the client")
        print("  - 'help' - Show this help message")
        print(f"  - Client ID: {self.client_id}")
        print(f"  - Router: {self.router_address}")
        print()


async def main() -> None:
    """Main entry point for the hydra-client-simple command."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Simple HydraRouter client for square calculations"
    )
    parser.add_argument(
        "--router-address",
        default="tcp://localhost:5556",
        help="Address of the HydraRouter (default: tcp://localhost:5556)",
    )
    parser.add_argument(
        "--client-id", help="Unique client identifier (auto-generated if not provided)"
    )
    parser.add_argument(
        "--number", type=int, help="Send single square request and exit"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Create and start client
    client = SimpleClient(router_address=args.router_address, client_id=args.client_id)

    try:
        await client.start()

        if args.number is not None:
            # Single request mode
            await client.send_square_request(args.number)
            # Wait a moment for response
            await asyncio.sleep(1)
        else:
            # Interactive mode
            await client.run_interactive()

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        await client.stop()


def sync_main() -> None:
    """Synchronous wrapper for main function."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sync_main()
