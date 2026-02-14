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
import time
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
        router_hb_port: int = DHydraRouter.HEARTBEAT_PORT,
        id: str = DModule.HYDRA_MQ
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
        self.hb_port = router_hb_port

        # Create async ZeroMQ context and DEALER socket
        self.ctx = zmq.asyncio.Context()
        self.socket = self.ctx.socket(zmq.DEALER)
        self.hb_socket = self.ctx.socket(zmq.DEALER)

        # Generate unique identity: base-id + random 4-char suffix
        self.identity = id

        # Set ZeroMQ socket identity (must be bytes)
        self.socket.setsockopt(zmq.IDENTITY, self.identity.encode("utf-8"))
        self.hb_socket.setsockopt(zmq.IDENTITY, self.identity.encode("utf-8"))

        # Build router address
        self.router_addr = f"tcp://{self.router}:{self.port}"
        self.router_hb_addr = f"tcp://{self.router}:{self.hb_port}"

        # Asyncio control events
        self.stop_event = asyncio.Event()
        self.heartbeat_stop_event = asyncio.Event()

        # Connect to router
        self.socket.connect(self.router_addr)
        self.hb_socket.connect(self.router_hb_addr)

        # Placeholder for heartbeat task
        self.heartbeat_task = None

        # A float holding time.time() for when the last heartbeat reply was received
        self._last_heartbeat = 0

    def connected(self) -> bool:
        if self._last_heartbeat == 0:
            return False

        interval = time.time() - self._last_heartbeat
        if interval > (2 * DHydra.HEARTBEAT_INTERVAL):
            return False
        
        return True
        

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

    async def send(self, msg: HydraMsg) -> None:
        """
        Send a HydraMsg through the router.

        Serializes the message to JSON and sends it through the
        DEALER socket to the connected ROUTER.

        Args:
            msg: HydraMsg instance to send

        Returns:
            None

        Raises:
            zmq.ZMQError: If send operation fails
        """
        # DEALER socket automatically prepends identity when sending to ROUTER
        await self.socket.send(msg.to_json())


    def start(self):
        # Start heartbeat task
        self.heartbeat_task = asyncio.create_task(self.start_heartbeat_bg())

    async def recv(self) -> HydraMsg:
        """
        Receive a HydraMsg from the router.

        Waits for an incoming message, deserializes it, and returns
        a HydraMsg instance.

        Args:
            timeout: Maximum time to wait for a message in seconds

        Returns:
            HydraMsg instance

        Raises:
            asyncio.TimeoutError: If no message received within timeout
            zmq.ZMQError: If receive operation fails
            json.JSONDecodeError: If message is not valid JSON
        """
        # DEALER socket receives single frame from ROUTER
        # ROUTER sends [client_identity, message], but DEALER
        # automatically strips the identity, leaving just [message]
        message_data = None
        message_data = await asyncio.wait_for(
            self.socket.recv(),
            timeout = DHydra.NETWORK_TIMEOUT
        )
        if message_data is not None:
            return HydraMsg.from_json(message_data)

    async def start_heartbeat_bg(self) -> None:
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
            )
            print(f"DEBUG: Sending heartbeat from {self.identity} to {self.router_hb_addr}")
            await self.hb_socket.send(msg.to_json())

            try:
                message_data = await asyncio.wait_for(
                    self.hb_socket.recv(),
                    timeout = DHydra.NETWORK_TIMEOUT
                )
                reply = HydraMsg.from_json(message_data)

                if reply.method == DMethod.HEARTBEAT_REPLY:
                    self._last_heartbeat = time.time()

            except asyncio.TimeoutError:
                # Just continue and try again
                pass

            await asyncio.sleep(DHydra.HEARTBEAT_INTERVAL)

