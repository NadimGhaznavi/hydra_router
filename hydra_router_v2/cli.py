"""
CLI - Command line interface for the Hydra Router system.

This module provides command-line tools for running the router and example
client/server applications with proper argument parsing and help documentation.
"""

import argparse
import asyncio
import sys

from .constants.DRouter import DRouter
from .hydra_router import HydraRouter  # type: ignore
from .simple_client import SimpleClient  # type: ignore
from .simple_server import SimpleServer  # type: ignore


def create_router_parser() -> argparse.ArgumentParser:
    """Create argument parser for router command."""
    parser = argparse.ArgumentParser(
        description="Hydra Router - ZeroMQ Message Router",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start router with default settings
  hydra-router

  # Start router on specific address and port
  hydra-router --address 0.0.0.0 --port 5557

  # Start router with debug logging
  hydra-router --log-level DEBUG

  # Start router with custom client limits
  hydra-router --max-clients 20 --heartbeat-timeout 60
        """,
    )

    parser.add_argument(
        "--address",
        default=DRouter.DEFAULT_ROUTER_ADDRESS,
        help=f"Router bind address (default: {DRouter.DEFAULT_ROUTER_ADDRESS})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DRouter.DEFAULT_ROUTER_PORT,
        help=f"Port to bind the router (default: {DRouter.DEFAULT_ROUTER_PORT})",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--max-clients",
        type=int,
        default=DRouter.MAX_CLIENTS,
        help=f"Maximum number of concurrent clients (default: {DRouter.MAX_CLIENTS})",
    )
    parser.add_argument(
        "--heartbeat-timeout",
        type=float,
        default=DRouter.DEFAULT_CLIENT_TIMEOUT,
        help=f"Client heartbeat timeout in seconds (default: {DRouter.DEFAULT_CLIENT_TIMEOUT})",
    )

    return parser


def create_client_parser() -> argparse.ArgumentParser:
    """Create argument parser for client command."""
    parser = argparse.ArgumentParser(
        description="Simple HydraRouter client for square calculations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start interactive client
  hydra-client

  # Connect to specific router
  hydra-client --router-address tcp://192.168.1.100:5556

  # Send single request and exit
  hydra-client --number 42

  # Enable debug logging
  hydra-client --log-level DEBUG
        """,
    )

    parser.add_argument(
        "--router-address",
        default=f"tcp://localhost:{DRouter.DEFAULT_ROUTER_PORT}",
        help=f"Address of the HydraRouter (default: tcp://localhost:{DRouter.DEFAULT_ROUTER_PORT})",
    )
    parser.add_argument(
        "--client-id",
        help="Unique client identifier (auto-generated if not provided)",
    )
    parser.add_argument(
        "--number",
        type=int,
        help="Send single square request and exit",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    return parser


def create_server_parser() -> argparse.ArgumentParser:
    """Create argument parser for server command."""
    parser = argparse.ArgumentParser(
        description="Simple HydraRouter server for square calculations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start server
  hydra-server

  # Connect to specific router
  hydra-server --router-address tcp://192.168.1.100:5556

  # Use custom server ID
  hydra-server --server-id my-calc-server

  # Enable debug logging
  hydra-server --log-level DEBUG
        """,
    )

    parser.add_argument(
        "--router-address",
        default=f"tcp://localhost:{DRouter.DEFAULT_ROUTER_PORT}",
        help=f"Address of the HydraRouter (default: tcp://localhost:{DRouter.DEFAULT_ROUTER_PORT})",
    )
    parser.add_argument(
        "--server-id",
        help="Unique server identifier (auto-generated if not provided)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    return parser


async def run_router(args: argparse.Namespace) -> None:
    """Run the Hydra Router."""
    router = HydraRouter(
        router_address=args.address,
        router_port=args.port,
        log_level=args.log_level,
        heartbeat_timeout=args.heartbeat_timeout,
        max_clients=args.max_clients,
    )

    try:
        print("🚀 Starting Hydra Router...")
        print(f"   Address: {args.address}")
        print(f"   Port: {args.port}")
        print(f"   Log Level: {args.log_level}")
        print(f"   Max Clients: {args.max_clients}")
        print(f"   Heartbeat Timeout: {args.heartbeat_timeout}s")
        print()

        await router.run_forever()

    except KeyboardInterrupt:
        print("\n🛑 Received shutdown signal")
    except Exception as e:
        print(f"❌ Router error: {e}")
        sys.exit(1)


async def run_client(args: argparse.Namespace) -> None:
    """Run the simple client."""
    client = SimpleClient(
        router_address=args.router_address,
        client_id=args.client_id,
        log_level=args.log_level,
    )

    try:
        await client.start()

        if args.number is not None:
            # Single request mode
            await client.send_square_request(args.number)
            # Wait a moment for response
            await asyncio.sleep(2)
        else:
            # Interactive mode
            await client.run_interactive()

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Client error: {e}")
        sys.exit(1)
    finally:
        await client.stop()


async def run_server(args: argparse.Namespace) -> None:
    """Run the simple server."""
    server = SimpleServer(
        router_address=args.router_address,
        server_id=args.server_id,
        log_level=args.log_level,
    )

    try:
        await server.start()
        await server.run()

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)
    finally:
        await server.stop()


def main_router() -> None:
    """Main entry point for hydra-router command."""
    parser = create_router_parser()
    args = parser.parse_args()

    try:
        asyncio.run(run_router(args))
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main_client() -> None:
    """Main entry point for hydra-client command."""
    parser = create_client_parser()
    args = parser.parse_args()

    try:
        asyncio.run(run_client(args))
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main_server() -> None:
    """Main entry point for hydra-server command."""
    parser = create_server_parser()
    args = parser.parse_args()

    try:
        asyncio.run(run_server(args))
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Default to router if run directly
    main_router()
