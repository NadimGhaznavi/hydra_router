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
import random
import string
from typing import Optional

import zmq
import zmq.asyncio

from hydra_router.constants.DHydra import (
    DHydra,
    DHydraRouter,
    DMethod,
    DModule,
)
from hydra_router.utils.HydraMsg import HydraMsg


class HydraMQ:
    """
    Async ZeroMQ client for HydraRouter communication.

    HydraMQ provides an async DEALER socket client that connects to a
    HydraRouter instance. It handles message serialization, heartbeats,
    and connection lifecycle.

    The client uses a DEALER socket which allows asynchronous bidirectional
    communication through a ROUTER-based message broker.

    Example:
        mq = HydraMQ(
            router_address="localhost",
            router_port=5757,
            id="my-service"
        )

        # Send message
        msg = HydraMsg(
            sender=mq.identity,
            target="other-service",
            method="ping",
            payload={"data": "test"}
        )
        await mq.send(msg)

        # Receive message
        response = await mq.recv()
        print(response.payload)

        # Cleanup
        await mq.quit()
    """

    def __init__(
        self,
        router_address: str = DHydraRouter.HOSTNAME,
        router_port: int = DHydraRouter.PORT,
        id: str = DModule.HYDRA_MQ,
        heartbeat_enabled: bool = True,
    ) -> None:
        """
        Initialize HydraMQ client.

        Args:
            router_address: Hostname/IP of the HydraRouter
            router_port: Port number of the HydraRouter
            id: Base identifier for this client (random suffix added)
            heartbeat_enabled: Whether to send periodic heartbeats

        Returns:
            None
        """
        self.router = router_address
        self.port = router_port
        self.heartbeat_enabled = heartbeat_enabled

        # Create async ZeroMQ context and DEALER socket
        self.ctx = zmq.asyncio.Context()
        self.socket = self.ctx.socket(zmq.DEALER)

        # Generate unique identity: base-id + random 4-char suffix
        random.seed(DHydra.RANDOM_SEED)
        chars = string.ascii_letters + string.digits
        rand_suffix = "".join(random.choice(chars) for _ in range(4))
        self.identity = f"{id}-{rand_suffix}"

        # Set ZeroMQ socket identity (must be bytes)
        self.socket.setsockopt(zmq.IDENTITY, self.identity.encode("utf-8"))

        # Build router address
        self.router_addr = f"tcp://{self.router}:{self.port}"

        # Asyncio control events
        self.stop_event = asyncio.Event()
        self.heartbeat_stop_event = asyncio.Event()

        # Connect to router
        self.socket.connect(self.router_addr)

        # Start heartbeat task if enabled
        self.heartbeat_task: Optional[asyncio.Task] = None
        if self.heartbeat_enabled:
            self.heartbeat_task = asyncio.create_task(
                self._send_heartbeat_loop()
            )

    async def send(self, msg: HydraMsg) -> None:
        """
        Send a HydraMsg through the router.

        Serializes the message to JSON and sends it as a multipart
        message with proper ZeroMQ envelope format.

        Args:
            msg: HydraMsg instance to send

        Returns:
            None

        Raises:
            zmq.ZMQError: If send operation fails
        """
        # DEALER socket multipart format: [empty_delimiter, message_data]
        # The socket automatically prepends our identity when sending
        await self.socket.send_multipart([b"", msg.to_json()])

    async def recv(self) -> HydraMsg:
        """
        Receive a HydraMsg from the router.

        Waits for an incoming message, deserializes it, and returns
        a HydraMsg instance.

        Returns:
            HydraMsg instance

        Raises:
            zmq.ZMQError: If receive operation fails
            json.JSONDecodeError: If message is not valid JSON
        """
        # DEALER socket receives: [empty_delimiter, message_data]
        # The router prepends sender identity, but DEALER strips it
        frames = await self.socket.recv_multipart()

        # frames[0] = empty delimiter
        # frames[1] = actual message data
        return HydraMsg.from_json(frames[1])

    async def _send_heartbeat_loop(self) -> None:
        """
        Periodic heartbeat loop to keep connection alive.

        Sends heartbeat messages to the router at regular intervals
        to indicate this client is still active.

        Returns:
            None
        """
        while not self.heartbeat_stop_event.is_set():
            msg = HydraMsg(
                sender=self.identity,
                target=DModule.HYDRA_ROUTER,
                method=DMethod.HEARTBEAT,
                payload={},
            )
            await self.send(msg)
            await asyncio.sleep(DHydra.HEARTBEAT_INTERVAL)

    async def quit(self) -> None:
        """
        Cleanly shutdown the HydraMQ client.

        Stops heartbeat task, disconnects from router, and cleans up
        ZeroMQ resources.

        Returns:
            None
        """
        # Stop heartbeat task
        if self.heartbeat_task is not None:
            self.heartbeat_stop_event.set()
            await asyncio.sleep(0.1)  # Give task time to exit
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass

        # Disconnect and cleanup
        try:
            self.socket.disconnect(self.router_addr)
            self.socket.close(linger=0)
        finally:
            self.ctx.term()
