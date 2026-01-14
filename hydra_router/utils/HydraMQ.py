# hydra_router/utils/HydraMQ.py
#
#    Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0
#

import asyncio
import zmq
import zmq.asyncio
import random
import sys
import random, string
from datetime import datetime

from hydra_router.constants.DHydra import DHydra, DHydraRouter, DModule, DMethod
from hydra_router.utils.HydraMsg import HydraMsg

class HydraMQ:
    """Manage the connection to the SimRouter."""

    def __init__(self, router_address=DHydraRouter.HOSTNAME, router_port=DHydraRouter.PORT, id=DModule.HYDRA_MQ ):
        self.router = router_address
        self.port = router_port
        self.ctx = zmq.asyncio.Context()
        self.socket = self.ctx.socket(zmq.DEALER)

        # Generate a random 4 character string
        random.seed(DHydra.RANDOM_SEED)
        CHARS = string.ascii_letters + string.digits
        rand_id = ''.join(random.choice(CHARS) for _ in range(4))

        # The ZeroMQ identity
        self.identity = id + "-" + rand_id

        # ZeroMQ socket type and identity
        self.socket.setsockopt(zmq.IDENTITY, self.identity)
        # ZeroMQ IP and port number
        self.router_addr = f"tcp://{self.router}:{self.port}"

        # Asyncio stop events
        self.stop_event = asyncio.Event()
        self.heartbeat_stop_event = asyncio.Event()

        # Connect
        self.socket.connect(self.router_addr)

        # Start sending heartbeat messages
        self.heartbeat_task = asyncio.create_task(self.send_heartbeat())

    async def send(self, msg):
        # Handy alias
        self.socket.send_json(msg.to_dict())

    async def send_heartbeat(self):
        """Periodic heartbeat to let the SimRouter know this client is alive."""
        while not self.heartbeat_stop_event.is_set():
            msg = HydraMsg(sender=self.identity.decode(), target=DModule.HYDRA_ROUTER, method=DMethod.HEARTBEAT)
            await self.send(msg)
            await asyncio.sleep(DHydra.HEARTBEAT_INTERVAL)

    async def quit(self):
        self.heartbeat_stop_event.set()
        await asyncio.sleep(DHydra.HEARTBEAT_INTERVAL)
        try:
            await self.socket.disconnect(self.router_addr)
            self.socket.close(linger=0)
        finally:
            self.ctx.term()

    async def recv(self):
        return await self.socket.recv_multipart()
