"""
Command-Line Interface for HydraRouter.

This module provides CLI commands for router deployment and management.
"""

import argparse
import asyncio
import signal
import sys
from typing import Optional

from .constants.DHydraLog import DHydraLog
from .router import HydraRouter
from .util.HydraLog import HydraLog


class HydraRouterCLI:
    """Command-line interface for HydraRouter management."""

    def __init__(self):
        """Initialize the CLI."""
        self.router: Optional[HydraRouter] = None
        self.running = False
        self.logger: Optional[HydraLog] = None

    async def start_router(self, args) -> None:
        """Start the HydraRouter with specified configuration.

        Args:
            args: Parsed command line arguments
        """
        # Setup logging with HydraLog
        self.logger = HydraLog("hydra-router-cli", to_console=True)

        # Convert CLI log level to DHydraLog format
        log_level_map = {
            "DEBUG": DHydraLog.DEBUG,
            "INFO": DHydraLog.INFO,
            "WARNING": DHydraLog.WARNING,
            "ERROR": DHydraLog.ERROR,
        }
        self.logger.loglevel(log_level_map.get(args.log_level, DHydraLog.INFO))

        self.logger.info("🚀 Starting HydraRouter...")
        self.logger.info(f"   Address: {args.address}")
        self.logger.info(f"   Port: {args.port}")
        self.logger.info(f"   Log Level: {args.log_level}")

        try:
            # Create and start router
            self.router = HydraRouter(address=args.address, port=args.port)
            await self.router.start()
            self.running = True

            self.logger.info("✅ HydraRouter started successfully!")
            self.logger.info(f"   Listening on: tcp://{args.address}:{args.port}")
            self.logger.info("   Press Ctrl+C to stop")

            # Setup signal handlers for graceful shutdown
            def signal_handler(signum, frame):
                self.logger.info(f"🛑 Received signal {signum}, shutting down...")
                self.running = False

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # Keep router running
            while self.running:
                await asyncio.sleep(1)

        except Exception as e:
            self.logger.error(f"❌ Failed to start router: {e}")
            sys.exit(1)
        finally:
            await self.stop_router()

    async def stop_router(self) -> None:
        """Stop the router gracefully."""
        if self.router and self.router.running:
            if self.logger:
                self.logger.info("🛑 Stopping HydraRouter...")
            await self.router.stop()
            if self.logger:
                self.logger.info("👋 HydraRouter stopped")
                self.logger.shutdown()

    async def show_status(self, args) -> None:
        """Show router status information.

        Args:
            args: Parsed command line arguments
        """
        # Setup logging for status command
        if not self.logger:
            self.logger = HydraLog("hydra-router-status", to_console=True)
            self.logger.loglevel(DHydraLog.INFO)

        self.logger.info("📊 HydraRouter Status")
        self.logger.info(f"   Router Address: {args.router_address}")

        # For now, just show connection attempt
        # In a full implementation, this would connect and query status
        try:
            self.logger.info("🔍 Attempting to connect to router...")
            self.logger.info("ℹ️  Status monitoring not yet implemented")
            self.logger.info("   This would show:")
            self.logger.info("   - Connected clients count")
            self.logger.info("   - Message throughput")
            self.logger.info("   - Uptime")
            self.logger.info("   - Memory usage")

        except Exception as e:
            self.logger.error(f"❌ Failed to connect to router: {e}")
            sys.exit(1)
        finally:
            if self.logger:
                self.logger.shutdown()


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI.

    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        prog="hydra-router",
        description="HydraRouter - ZeroMQ-based message routing system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start router on default address and port
  hydra-router start

  # Start router on specific address and port
  hydra-router start --address 0.0.0.0 --port 5557

  # Start router with debug logging
  hydra-router start --log-level DEBUG

  # Check router status
  hydra-router status --router-address tcp://localhost:5556

  # Show help
  hydra-router --help
        """,
    )

    # Global options
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    # Subcommands
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", metavar="COMMAND"
    )

    # Start command
    start_parser = subparsers.add_parser(
        "start",
        help="Start the HydraRouter",
        description="Start the HydraRouter with specified configuration",
    )
    start_parser.add_argument(
        "--address",
        default="127.0.0.1",
        help="Address to bind the router (default: 127.0.0.1)",
    )
    start_parser.add_argument(
        "--port", type=int, default=5556, help="Port to bind the router (default: 5556)"
    )
    start_parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    # Status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show router status",
        description="Show status information for a running HydraRouter",
    )
    status_parser.add_argument(
        "--router-address",
        default="tcp://localhost:5556",
        help="Address of the running router (default: tcp://localhost:5556)",
    )

    return parser


async def async_main() -> None:
    """Async main function."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = HydraRouterCLI()

    try:
        if args.command == "start":
            await cli.start_router(args)
        elif args.command == "status":
            await cli.show_status(args)
        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the hydra-router command."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
