#!/usr/bin/env python3
"""
Simple Square Calculation Demo for HydraRouter.

This is a complete walkthrough example that demonstrates the basic square
calculation functionality using the SimpleClient and SimpleServer classes.
This example shows the most straightforward usage of the HydraRouter system.

Usage:
    1. Start the router: python -m hydra_router.cli start
    2. Run this demo: python examples/simple_square_demo.py
"""

import asyncio

from hydra_router.simple_client import SimpleClient
from hydra_router.simple_server import SimpleServer


async def run_demo_server():
    """Run the demo server."""
    print("🔢 Starting Demo Server...")

    server = SimpleServer(
        router_address="tcp://localhost:5556", server_id="demo-server"
    )

    try:
        await server.start()

        # Run server for the demo duration
        print("✅ Demo server is ready to process requests")

        # Keep server running
        for i in range(30):  # Run for 30 seconds
            await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ Demo server error: {e}")
    finally:
        await server.stop()


async def run_demo_client():
    """Run the demo client."""
    # Wait a moment for server to start
    await asyncio.sleep(2)

    print("📱 Starting Demo Client...")

    client = SimpleClient(
        router_address="tcp://localhost:5556", client_id="demo-client"
    )

    try:
        await client.start()
        print("✅ Demo client connected")

        # Demo sequence: calculate squares of various numbers
        demo_numbers = [1, 2, 3, 5, 8, 13, 21]

        print(f"\n🎯 Demo: Calculating squares of {demo_numbers}")
        print("-" * 50)

        for number in demo_numbers:
            print(f"\n📤 Requesting: {number}²")
            await client.send_square_request(number)

            # Wait for response
            await asyncio.sleep(1.5)

        print("\n✅ Demo sequence completed!")

        # Wait a bit more for any remaining responses
        await asyncio.sleep(2)

    except Exception as e:
        print(f"❌ Demo client error: {e}")
    finally:
        await client.stop()


async def interactive_demo():
    """Run an interactive demo where user can input numbers."""
    print("\n🎮 Interactive Demo Mode")
    print("-" * 30)

    client = SimpleClient(
        router_address="tcp://localhost:5556", client_id="interactive-demo-client"
    )

    try:
        await client.start()

        print("Enter numbers to calculate their squares (or 'quit' to exit):")

        while True:
            try:
                user_input = input("\nEnter a number: ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    break

                number = int(user_input)
                await client.send_square_request(number)

                # Wait for response
                await asyncio.sleep(1)

            except ValueError:
                print("❌ Please enter a valid integer")
            except KeyboardInterrupt:
                print("\n🛑 Interactive demo interrupted")
                break

    except Exception as e:
        print(f"❌ Interactive demo error: {e}")
    finally:
        await client.stop()


async def main():
    """Main demo function."""
    print("🚀 Simple Square Calculation Demo")
    print("=" * 50)
    print("This demo shows the basic HydraRouter functionality.")
    print("Make sure to start the router first:")
    print("  python -m hydra_router.cli start")
    print()

    try:
        print("🎬 Starting automated demo...")

        # Run server and client concurrently for automated demo
        server_task = asyncio.create_task(run_demo_server())
        client_task = asyncio.create_task(run_demo_client())

        # Wait for client to complete
        await client_task

        # Cancel server task
        server_task.cancel()

        try:
            await server_task
        except asyncio.CancelledError:
            pass

        print("\n" + "=" * 50)
        print("🎉 Automated demo completed!")

        # Ask if user wants interactive mode
        try:
            response = (
                input("\nWould you like to try interactive mode? (y/n): ")
                .strip()
                .lower()
            )
            if response in ["y", "yes"]:
                # Start server for interactive mode
                server_task = asyncio.create_task(run_demo_server())

                # Wait a moment for server to start
                await asyncio.sleep(1)

                # Run interactive demo
                await interactive_demo()

                # Stop server
                server_task.cancel()
                try:
                    await server_task
                except asyncio.CancelledError:
                    pass

        except (KeyboardInterrupt, EOFError):
            print("\n🛑 Demo ended")

        print("\n👋 Demo finished. Thank you for trying HydraRouter!")

    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
