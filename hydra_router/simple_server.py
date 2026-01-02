"""
SimpleServer - Example server application for the Hydra Router system.

This module provides a simple server that connects to a HydraRouter and processes
square calculation requests from clients. It demonstrates basic usage of the MQClient
library for server applications.
"""

import asyncio
import signal
import sys
import time
from types import FrameType
from typing import Any, Dict, Optional

from .constants.DHydraLog import DHydraLog
from .constants.DMsgType import DMsgType
from .constants.DRouter import DRouter
from .mq_client import MQClient, ZMQMessage
from .util.HydraLog import HydraLog


class SimpleServer:
    """Simple server for processing square calculation requests."""

    def __init__(
        self,
        router_address: str = "tcp://localhost:5556",
        server_id: Optional[str] = None,
        enable_stats: bool = False,
    ):
        """Initialize the simple server.

        Args:
            router_address: Address of the HydraRouter
            server_id: Unique server identifier (auto-generated if None)
            enable_stats: Whether to enable periodic statistics display
        """
        self.router_address = router_address
        self.server_id = server_id or f"simple-server-{int(time.time())}"
        self.client = MQClient(
            router_address=router_address,
            client_type=DRouter.SIMPLE_SERVER,
            client_id=self.server_id,
            enable_stats=enable_stats,
        )
        self.running = False
        self.request_count = 0
        self.logger = HydraLog(f"simple_server_{self.server_id}", to_console=True)
        self.logger.loglevel(DHydraLog.INFO)

        # Set up custom heartbeat data provider
        self.client.set_heartbeat_data_provider(self._get_heartbeat_data)

    async def start(self) -> None:
        """Start the server and connect to router."""
        try:
            await self.client.connect()
            self.running = True
            self.logger.info(
                f"Simple server {self.server_id} connected to {self.router_address}"
            )
            print(f"✅ Server connected to router at {self.router_address}")
            print(f"Server ID: {self.server_id}")
            print("🔢 Ready to process square calculation requests...")

            # Register request handler
            self.client.register_message_handler(
                DMsgType.SQUARE_REQUEST, self._handle_square_request
            )

        except Exception as e:
            self.logger.error(f"Failed to connect to router: {e}")
            print(f"❌ Failed to connect to router: {e}")
            raise

    def _get_heartbeat_data(self) -> Dict[str, Any]:
        """Provide custom data for heartbeat messages."""
        return {
            "requests_processed": self.request_count,
            "server_status": "processing" if self.running else "stopped",
        }

    async def stop(self) -> None:
        """Stop the server and disconnect from router."""
        self.running = False
        if self.client.connected:
            await self.client.disconnect()
            self.logger.info(f"Simple server {self.server_id} disconnected")
            print(f"👋 Server disconnected (processed {self.request_count} requests)")

    async def _handle_square_request(self, message: ZMQMessage) -> None:
        """Handle square calculation request.

        Args:
            message: Request message from client
        """
        try:
            data = message.data or {}
            number = data.get("number")
            request_id = message.request_id
            client_id = message.client_id

            if number is None:
                self.logger.warning(f"Invalid request from {client_id}: missing number")
                print(f"⚠️  Invalid request from {client_id}: missing number")
                return

            # Calculate square
            result = number * number
            self.request_count += 1

            self.logger.info(
                f"Processing request from {client_id}: {number}² = {result}"
            )
            print(
                f"📥 Request #{self.request_count}: {number}² = {result} (from {client_id})"
            )

            # Send response
            response = ZMQMessage(
                message_type=DMsgType.SQUARE_RESPONSE,
                timestamp=time.time(),
                client_id=self.server_id,
                request_id=request_id,
                data={"number": number, "result": result, "server_id": self.server_id},
            )

            await self.client.send_message(response)
            print(f"📤 Response sent: {number}² = {result}")

        except Exception as e:
            self.logger.error(f"Error handling square request: {e}")
            print(f"❌ Error processing request: {e}")

    async def run(self) -> None:
        """Run the server and wait for shutdown signal."""
        print("\n🚀 Simple Square Calculator Server")
        print("=" * 40)
        print("Waiting for square calculation requests...")
        print("Press Ctrl+C to stop")
        print()

        # Setup signal handlers for graceful shutdown
        def signal_handler(signum: int, frame: Optional[FrameType]) -> None:
            print(f"\n🛑 Received signal {signum}, shutting down...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            # Just wait for shutdown - MQClient handles heartbeats automatically
            while self.running:
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            self.logger.info("Server task cancelled")
        except Exception as e:
            self.logger.error(f"Error in server run loop: {e}")
            print(f"❌ Server error: {e}")
        finally:
            await self.stop()


async def main() -> None:
    """Main entry point for the hydra-server-simple command."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Simple HydraRouter server for square calculations"
    )
    parser.add_argument(
        "--router-address",
        default="tcp://localhost:5556",
        help="Address of the HydraRouter (default: tcp://localhost:5556)",
    )
    parser.add_argument(
        "--server-id", help="Unique server identifier (auto-generated if not provided)"
    )
    parser.add_argument(
        "--stats", action="store_true", help="Display periodic statistics"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Create and start server
    server = SimpleServer(
        router_address=args.router_address,
        server_id=args.server_id,
        enable_stats=args.stats,
    )

    try:
        await server.start()
        await server.run()

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        await server.stop()


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
