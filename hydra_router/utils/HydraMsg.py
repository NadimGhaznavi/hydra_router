# hydra_router/utils/HydraMsg.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

import json
import uuid
from typing import Any, Dict, Optional

from hydra_router.constants.DHydra import DHydra, DHydraMsg


class HydraMsg:
    """
    Structured message class for HydraRouter communication protocol.

    HydraMsg encapsulates messages for ZeroMQ-based RPC communication.
    It handles serialization/deserialization and provides a clean API
    for creating and accessing message components.

    Internal representation uses Python objects (dict for payload).
    Serialization to JSON happens only when converting to wire format.

    Example:
        # Create message
        msg = HydraMsg(
            sender="client-123",
            target="service-x",
            method="ping",
            payload={"sequence": 1, "data": "test"}
        )

        # Serialize for transmission
        json_bytes = msg.to_json()

        # Deserialize from received data
        msg = HydraMsg.from_json(json_bytes)
    """

    def __init__(
        self,
        sender: Optional[str] = None,
        target: Optional[str] = None,
        method: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        msg_id: Optional[str] = None,
    ) -> None:
        """
        Initialize a new HydraMsg instance.

        Args:
            sender: Identifier of the message sender
            target: Identifier of the intended message recipient
            method: RPC method or action to be performed
            payload: Message data as a dictionary (not JSON string)
            msg_id: Unique message identifier (auto-generated if None)

        Returns:
            None
        """
        self._sender = sender
        self._target = target
        self._method = method
        self._payload = payload if payload is not None else {}
        self._id = msg_id if msg_id is not None else str(uuid.uuid4())

    @property
    def sender(self) -> Optional[str]:
        """Get the message sender identifier."""
        return self._sender

    @sender.setter
    def sender(self, value: str) -> None:
        """Set the message sender identifier."""
        self._sender = value

    @property
    def target(self) -> Optional[str]:
        """Get the message target identifier."""
        return self._target

    @target.setter
    def target(self, value: str) -> None:
        """Set the message target identifier."""
        self._target = value

    @property
    def method(self) -> Optional[str]:
        """Get the RPC method name."""
        return self._method

    @method.setter
    def method(self, value: str) -> None:
        """Set the RPC method name."""
        self._method = value

    @property
    def payload(self) -> Dict[str, Any]:
        """Get the message payload as a dictionary."""
        return self._payload

    @payload.setter
    def payload(self, value: Dict[str, Any]) -> None:
        """Set the message payload from a dictionary."""
        self._payload = value

    @property
    def id(self) -> str:
        """Get the unique message identifier."""
        return self._id

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HydraMsg":
        """
        Create a HydraMsg from a dictionary.

        Args:
            data: Dictionary containing message fields

        Returns:
            HydraMsg instance

        Raises:
            KeyError: If required fields are missing
        """
        return cls(
            sender=data.get(DHydraMsg.SENDER),
            target=data.get(DHydraMsg.TARGET),
            method=data.get(DHydraMsg.METHOD),
            payload=data.get(DHydraMsg.PAYLOAD, {}),
            msg_id=data.get(DHydraMsg.ID),
        )

    @classmethod
    def from_json(cls, json_data: bytes) -> "HydraMsg":
        """
        Create a HydraMsg from JSON bytes.

        Args:
            json_data: JSON-encoded message as bytes

        Returns:
            HydraMsg instance

        Raises:
            json.JSONDecodeError: If json_data is not valid JSON
            UnicodeDecodeError: If json_data cannot be decoded as UTF-8
        """
        if isinstance(json_data, bytes):
            json_data = json_data.decode("utf-8")
        return cls.from_dict(json.loads(json_data))

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert message to dictionary representation.

        Returns:
            Dictionary containing all message fields including version
        """
        return {
            DHydraMsg.ID: self._id,
            DHydraMsg.SENDER: self._sender,
            DHydraMsg.TARGET: self._target,
            DHydraMsg.METHOD: self._method,
            DHydraMsg.PAYLOAD: self._payload,
            DHydraMsg.V: DHydra.PROTOCOL_VERSION,
        }

    def to_json(self) -> bytes:
        """
        Convert message to JSON bytes for transmission.

        Returns:
            JSON-encoded message as UTF-8 bytes ready for ZeroMQ

        Raises:
            TypeError: If message contains non-serializable objects
        """
        return json.dumps(self.to_dict()).encode("utf-8")

    def __repr__(self) -> str:
        """
        Return string representation of message for debugging.

        Returns:
            String showing message structure
        """
        return (
            f"HydraMsg(id={self._id}, sender={self._sender}, "
            f"target={self._target}, method={self._method})"
        )

    def __str__(self) -> str:
        """
        Return human-readable string representation.

        Returns:
            Formatted string with message details
        """
        return (
            f"HydraMsg: {self._sender} -> {self._target} "
            f"[{self._method}] (id: {self._id})"
        )
