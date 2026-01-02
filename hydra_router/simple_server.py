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
from typing import Optional

from .constants.DHydraLog import DHydraLog
from .constants.DRouter import DRouter
from .mq_client import MessageType, MQClient, ZMQMessage
from .util.HydraLog import HydraLog


class SimpleServer:
    """Simple server for processing square calculation requests."""

    def __init__(
        self,
        router_address: str = "tcp://localhost:5556",
        server_id: Optional[str] = None,
    ):
        """Initialize the simple server.

        Args:
            router_address: Address of the HydraRouter
            server_id: Unique server identifier (auto-generated if None)
        """
        self.router_address = router_address
        self.server_id = server_id or f"simple-server-{int(time.time())}"
        self.client = MQClient(
            router_address=router_address,
            client_type=DRouter.SIMPLE_SERVER,
            client_id=self.server_id,
        )
        self.running = False
        self.request_count = 0
        self.logger = HydraLog(f"simple_server_{self.server_id}", to_console=True)
        self.logger.loglevel(DHydraLog.INFO)

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
                MessageType.SQUARE_REQUEST, self._handle_square_request
            )

            # Start heartbeat
            await self._send_heartbeat()

        except Exception as e:
            self.logger.error(f"Failed to connect to router: {e}")
            print(f"❌ Failed to connect to router: {e}")
            raise

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
                message_type=MessageType.SQUARE_RESPONSE,
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

    async def _send_heartbeat(self) -> None:
        """Send periodic heartbeat to router."""
        try:
            heartbeat = ZMQMessage(
                message_type=MessageType.HEARTBEAT,
                timestamp=time.time(),
                client_id=self.server_id,
                data={"status": "alive", "requests_processed": self.request_count},
            )

            await self.client.send_message(heartbeat)
            self.logger.debug(f"Sent heartbeat from {self.server_id}")

        except Exception as e:
            self.logger.error(f"Error sending heartbeat: {e}")

    async def run(self) -> None:
        """Run the server with periodic heartbeat."""
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
            while self.running:
                # Send periodic heartbeat
                await self._send_heartbeat()

                # Wait before next heartbeat
                await asyncio.sleep(30)  # Heartbeat every 30 seconds

        except asyncio.CancelledError:
            self.logger.info("Server task cancelled")
        except Exception as e:
            self.logger.error(f"Error in server run loop: {e}")
            print(f"❌ Server error: {e}")
        finally:
            await self.stop()

    async def run_with_stats(self) -> None:
        """Run server with periodic statistics display."""
        stats_task = asyncio.create_task(self._stats_loop())
        server_task = asyncio.create_task(self.run())

        try:
            await asyncio.gather(server_task, stats_task)
        except Exception as e:
            self.logger.error(f"Error in server with stats: {e}")
        finally:
            stats_task.cancel()
            server_task.cancel()

    async def _stats_loop(self) -> None:
        """Display periodic statistics."""
        start_time = time.time()

        while self.running:
            await asyncio.sleep(60)  # Stats every minute

            if self.running:
                uptime = time.time() - start_time
                uptime_str = f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s"
                rate = self.request_count / uptime if uptime > 0 else 0

                print(
                    f"📊 Stats: {self.request_count} requests processed, "
                    f"uptime: {uptime_str}, rate: {rate:.2f} req/s"
                )


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
    server = SimpleServer(router_address=args.router_address, server_id=args.server_id)

    try:
        await server.start()

        if args.stats:
            await server.run_with_stats()
        else:
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
