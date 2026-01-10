# hydra_router/client/HydraClient.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

from typing import Optional

import zmq

from hydra_router.utils.HydraLog import HydraLog
from hydra_router.constants.DHydra import DHydraClientMsg, DHydraServerDef, DModule


class HydraClient:
    """
    Abstract base class for HydraClient implementations.

    Provides common ZeroMQ-based client functionality that connects to a server
    and sends requests using the REQ/REP pattern. Subclasses must implement
    application-specific message handling logic.
    """

    def __init__(
        self,
        server_hostname: Optional[str] = None,
        server_port: Optional[int] = None,
        id: Optional[str] = DModule.HYDRA_CLIENT,
    ) -> None:
        """
        Initialize the HydraClient with server connection parameters.

        Args:
            server_hostname (str): The server hostname to connect to
            server_port (int): The server port to connect to
            client_id (str): Identifier for logging purposes
        """
        self._server_hostname = server_hostname or DHydraServerDef.HOSTNAME
        self._server_port = server_port or DHydraServerDef.PORT
        self._id = id

        self.server_address = (
            "tcp://" + self._server_hostname + ":" + str(self._server_port)
        )
        self.context: Optional[zmq.Context] = None
        self.socket: Optional[zmq.Socket] = None
        self._setup_socket()

    def loglevel(self, log_level: str) -> None:
        """
                Docstring for _init_log

                :param self: Description
                :param log_id: Description
                :type log_id: str
                :param log_level: Description(hydra_venv) dan@sally:~/dev/hydra_router$ hydra-pong-server --log-level DEBUG
        HydraServer error: 30

                :type log_level: str
        """
        self.log = HydraLog(client_id=self._id, log_level=log_level, to_console=True)

    def _setup_socket(self) -> None:
        """
        Set up ZeroMQ context and REQ socket with connection.

        Creates a new ZeroMQ context and REQ socket, then connects to the
        configured server address. Logs connection success or exits on failure.

        Returns:
            None

        Raises:
            Exception: If socket creation or connection fails
        """
        try:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect(self.server_address)
            self.log.info(
                DHydraClientMsg.CONNECTED.format(server_address=self.server_address)
            )
        except Exception as e:
            self.log.error(DHydraClientMsg.ERROR.format(e=e))
            exit(1)

    def send_message(self, message: bytes) -> bytes:
        """
        Send a message to the server and wait for response.

        Sends a message to the connected server using the REQ/REP pattern
        and blocks until a response is received. Logs the message exchange
        for debugging purposes.

        Args:
            message (bytes): The message to send to the server

        Returns:
            bytes: The response received from the server

        Raises:
            RuntimeError: If socket is not initialized
            Exception: If message sending or receiving fails
        """
        try:
            self.log.debug(DHydraClientMsg.SENDING.format(message=message))
            if self.socket is not None:
                self.socket.send(message)

                # Wait for response
                response: bytes = self.socket.recv()
                self.log.debug(DHydraClientMsg.RECEIVED.format(response=response))
                return response
            else:
                raise RuntimeError("Socket not initialized")

        except Exception as e:
            self.log.error(DHydraClientMsg.ERROR.format(e=e))
            exit(1)

    def _cleanup(self) -> None:
        """
        Clean up ZeroMQ resources.

        Properly closes the socket and terminates the ZeroMQ context
        to prevent resource leaks. Should be called when the client
        is no longer needed.

        Returns:
            None
        """
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()
        self.log.info(DHydraClientMsg.CLEANUP)

    def run(self) -> None:
        """
        Abstract method that subclasses must implement to define
        application-specific client behavior.
        """
        raise NotImplementedError("This should be implemented in the child class")
