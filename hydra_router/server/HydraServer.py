# hydra_router/server/HydraServer.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

from typing import Optional

import asyncio
import argparse
import os
import sys

if __package__ in (None, ""):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from hydra_router.utils.HydraLog import HydraLog
from hydra_router.utils.HydraMQ import HydraMQ, HydraMsg
from hydra_router.constants.DHydra import (
    DHydraLogDef,
    DHydraRouterDef,
    DHydraServerDef,
    DModule,
    DMethod,
)


class HydraServer:
    """
    Abstract base class for HydraServer implementations.

    Provides common ZeroMQ-based server functionality that binds to a port
    and handles client requests using the REQ/REP pattern. Subclasses must
    implement application-specific message handling logic.
    """

    def __init__(
        self,
        address: str = "*",
        port: int = DHydraServerDef.PORT,
        router_address: str = DHydraRouterDef.HOSTNAME,
        router_port: int = DHydraRouterDef.PORT,
        id: Optional[str] = DModule.HYDRA_SERVER,
        log_level: Optional[str] = DHydraLogDef.DEFAULT_LOG_LEVEL,
    ):
        """
        Initialize the HydraServer with binding parameters.

        Args:
            address (str): The address to bind to (default: "*" for all interfaces)
            port (int): The port to bind to
            server_id (str): Identifier for logging purposes
        """

        self.address = address
        self.port = port
        self.router_address = router_address
        self.router_port = router_port
        self.id = id
        self._methods = {
            DMethod.PING: self.ping,
        }
        self.mq: Optional[HydraMQ] = None
        self.log = HydraLog(client_id=self.id, log_level=log_level, to_console=True)
        self.main_loop()

    def main_loop(self) -> None:
        asyncio.run(self._main_loop())

    async def _main_loop(self) -> None:
        self.mq = HydraMQ(
            router_address=self.router_address,
            router_port=self.router_port,
            id=self.id,
            srv_methods=self._methods,
        )
        self.mq.start()
        while True:
            await asyncio.sleep(1)

    async def ping(self, msg: HydraMsg):
        self.log.info(f"Received ping from {msg.sender}")
        reply_msg = HydraMsg(
            sender=DModule.HYDRA_SERVER,
            target=msg.sender,
            method=DMethod.PONG,
        )
        if self.mq is not None:
            await self.mq.send(reply_msg)
            self.log.info(f"Sent pong to {msg.sender}")

    def loglevel(self, log_level: str) -> None:
        """
        Initialize console logging for the server instance.
        """
        self.log = HydraLog(client_id=self.id, log_level=log_level, to_console=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Hydra ZeroMQ server")
    parser.add_argument("--address", default="*", help="Address to bind to")
    parser.add_argument(
        "--log_level",
        default=DHydraLogDef.DEFAULT_LOG_LEVEL,
        help="Log level [DEBUG|INFO|WARNING|ERROR|CRITICAL]",
    )
    parser.add_argument(
        "--port", type=int, default=DHydraServerDef.PORT, help="Server port"
    )
    parser.add_argument(
        "--router-address",
        default=DHydraRouterDef.HOSTNAME,
        help="HydraRouter hostname",
    )
    parser.add_argument(
        "--router-port",
        type=int,
        default=DHydraRouterDef.PORT,
        help="HydraRouter main port",
    )
    parser.add_argument("--id", default=DModule.HYDRA_SERVER, help="Server identity")
    args = parser.parse_args()

    HydraServer(
        address=args.address,
        port=args.port,
        router_address=args.router_address,
        router_port=args.router_port,
        id=args.id,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()
