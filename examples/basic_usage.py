#!/usr/bin/env python3
"""
Basic usage example for Hydra Router.

This example will be expanded as components are implemented.
"""

import asyncio

from hydra_router.mq_client import MQClient
from hydra_router.router import HydraRouter


async def main() -> None:
    """Demonstrate basic usage example."""
    print("Hydra Router Basic Usage Example")
    print("================================")

    # Demonstrate MQClient creation
    print("Creating MQClient")
    client = MQClient(
        router_address="tcp://localhost:5556",
        client_type="SimpleClient",
        client_id="basic-usage-demo",
    )

    print(f"✓ MQClient created: {client}")
    print(f"✓ HydraRouter class: {HydraRouter}")
    print(f"✓ MQClient class: {MQClient}")
    print("✓ DRouter constants: Available via hydra_router.constants.DRouter")
    print("✓ Basic usage demonstration complete")


if __name__ == "__main__":
    asyncio.run(main())
