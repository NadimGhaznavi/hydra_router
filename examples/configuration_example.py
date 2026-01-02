#!/usr/bin/env python3
"""
Configuration Example for HydraRouter.

This example demonstrates different configuration options and deployment
scenarios for the HydraRouter system, including various network configurations,
client types, and deployment patterns.

Usage:
    python examples/configuration_example.py
"""

import asyncio

from hydra_router.router import HydraRouter
from hydra_router.router_constants import RouterConstants


async def example_basic_configuration():
    """Example of basic router configuration."""
    print("🔧 Basic Configuration Example")
    print("-" * 40)

    # Basic router with default settings
    router = HydraRouter()
    print(f"Default address: {router.address}")
    print(f"Default port: {router.port}")

    # Custom configuration
    custom_router = HydraRouter(address="0.0.0.0", port=5557)
    print(f"Custom address: {custom_router.address}")
    print(f"Custom port: {custom_router.port}")


async def example_client_configuration():
    """Example of client configuration options."""
    print("\n📱 Client Configuration Example")
    print("-" * 40)

    # Different client types
    client_configs = [
        {
            "type": RouterConstants.HYDRA_CLIENT,
            "id": "hydra-client-001",
            "description": "Standard Hydra client",
        },
        {
            "type": RouterConstants.SIMPLE_CLIENT,
            "id": "simple-client-001",
            "description": "Simple calculation client",
        },
        {
            "type": RouterConstants.HYDRA_SERVER,
            "id": "hydra-server-001",
            "description": "Standard Hydra server",
        },
        {
            "type": RouterConstants.SIMPLE_SERVER,
            "id": "simple-server-001",
            "description": "Simple calculation server",
        },
    ]

    for config in client_configs:
        print(f"Client Type: {config['type']}")
        print(f"  ID: {config['id']}")
        print(f"  Description: {config['description']}")
        print()


async def example_network_configuration():
    """Example of network configuration options."""
    print("🌐 Network Configuration Example")
    print("-" * 40)

    # Different network configurations
    network_configs = [
        {"address": "tcp://localhost:5556", "description": "Local development"},
        {
            "address": "tcp://0.0.0.0:5556",
            "description": "Accept connections from any interface",
        },
        {
            "address": "tcp://192.168.1.100:5556",
            "description": "Specific network interface",
        },
        {
            "address": "ipc:///tmp/hydra-router.sock",
            "description": "Unix domain socket (local only)",
        },
    ]

    for config in network_configs:
        print(f"Address: {config['address']}")
        print(f"  Use case: {config['description']}")
        print()


async def main():
    """Main configuration example."""
    print("🚀 HydraRouter Configuration Examples")
    print("=" * 50)

    await example_basic_configuration()
    await example_client_configuration()
    await example_network_configuration()

    print("✅ Configuration examples completed!")
    print("\nFor deployment, use the CLI:")
    print("  hydra-router start --address 0.0.0.0 --port 5556")


if __name__ == "__main__":
    asyncio.run(main())
