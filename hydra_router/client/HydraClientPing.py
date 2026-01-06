#!/usr/bin/env python

# hydra_router/client/HydraClientPing.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

import argparse
import sys
from typing import Optional

import zmq

from hydra_router.constants.DHydra import HydraMsg, DHydraServerDef, DModule
from hydra_router.utils.HydraLog import HydraLog
from hydra_router.utils.HydraMsg import HydraMsg
from hydra_router.client.HydraClient import HydraClient


class HydraClientPing(HydraClient):
    """
    HydraClientPing uses the HydraClient to create a simple "ping-client" that
    connects to a "pong-server", sends a "ping" and -hopefully- displays a "pong"
    from the "pong-server".
    """

    def __init__(
        self,
        server_hostname: Optional[str] = None,
        server_port: Optional[int] = None,
        client_id: Optional[str] = None,
    ) -> None:
        """
        Initialize the HydraClient with server connection parameters.

        Args:
            server_address (str): The server address to connect to
                (default: "tcp://localhost:5555")
        """
        client_id = client_id or DModule.HYDRA_CLIENT

        self.log = HydraLog(client_id=client_id, to_console=True)

        self._server_hostname = server_hostname or DHydraServerDef.HOSTNAME
        self._server_port = server_port or DHydraServerDef.PORT

        self.server_address = (
            "tcp://" + self._server_hostname + ":" + str(self._server_port)
        )
        self.context: Optional[zmq.Context] = None
        self.socket: Optional[zmq.Socket] = None
        self._setup_socket()

    def _setup_socket(self) -> None:
        """Set up ZeroMQ context and REQ socket with connection."""
        try:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect(self.server_address)
            self.log.info(HydraMsg.CONNECTED.format(server_address=self.server_address))
        except Exception as e:
            self.log.error(HydraMsg.ERROR.format(e=e))
            exit(1)

    def send_message(self, message: bytes) -> bytes:
        """
        Send a message to the server and wait for response.

        Args:
            message (bytes): The message to send to the server

        Returns:
            bytes: The response received from the server
        """
        try:
            self.log.debug(HydraMsg.SENDING.format(message=message))
            if self.socket is not None:
                self.socket.send(message)

                # Wait for response
                response: bytes = self.socket.recv()
                self.log.debug(HydraMsg.RECEIVED.format(response=response))
                return response
            else:
                raise RuntimeError("Socket not initialized")

        except Exception as e:
            self.log.error(HydraMsg.ERROR.format(e=e))
            exit(1)

    def _cleanup(self) -> None:
        """Clean up ZeroMQ resources."""
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()
        print(HydraMsg.CLEANUP)


def main() -> None:
    """Main entry point for hydra-client command."""
    parser = argparse.ArgumentParser(
        description="Connect to a HydraServer and send messages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hydra-client                          # Send "Hello" to localhost:5757
  hydra-client --hostname 192.168.1.100  # Connect to remote server
  hydra-client --port 8080              # Connect to different port
  hydra-client --message "Test message" # Send custom message
  hydra-client --count 5                # Send 5 messages
  hydra-client --hostname server.com --port 9000 --message "Custom" --count 3
        """,
    )

    parser.add_argument(
        "--hostname",
        "-H",
        default=DHydraServerDef.HOSTNAME,
        help=HydraMsg.SERVER_HELP.format(server_address=DHydraServerDef.HOSTNAME),
    )

    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=DHydraServerDef.PORT,
        help=HydraMsg.PORT_HELP.format(server_port=DHydraServerDef.PORT),
    )

    parser.add_argument(
        "--message",
        "-m",
        default="Hello",
        help="Message to send to server (default: 'Hello')",
    )

    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=1,
        help="Number of messages to send (default: 1)",
    )

    parser.add_argument("--version", "-v", action="version", version="ai-hydra 0.1.0")

    args = parser.parse_args()

    try:
        print(f"Connecting to HydraServer at {args.hostname}:{args.port}")

        client = HydraClient(server_hostname=args.hostname, server_port=args.port)

        for i in range(args.count):
            if args.count > 1:
                print(f"\n--- Message {i + 1}/{args.count} ---")

            message = args.message.encode("utf-8")
            response = client.send_message(message)

            if args.count > 1:
                decoded_response = response.decode("utf-8", errors="replace")
                print(f"Response {i + 1}: {decoded_response}")

        client._cleanup()
        print("\nClient session completed successfully")

    except KeyboardInterrupt:
        print("\nClient stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Client error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
