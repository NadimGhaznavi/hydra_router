# hydra_router/utils/HydraMsg.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

import uuid
import json
from typing import Optional, Dict, Any

from hydra_router.constants.DHydra import DHydra, DHydraMsg


class HydraMsg:
    """
    Structured message class for HydraRouter communication protocol.

    HydraMsg provides a standardized message format for communication between
    HydraClient and HydraServer instances. Each message contains sender/target
    identification, method specification, and optional payload data.
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
            sender (Optional[str]): Identifier of the message sender
            target (Optional[str]): Identifier of the intended message recipient
            method (Optional[str]): Method or action to be performed
            payload (Optional[str]): Message data or parameters as JSON string

        Returns:
            None
        """
        self._sender = sender
        self._target = target
        self._method = method

        self._payload = payload or {}
        self._id = msg_id or uuid.uuid4()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HydraMsg":
        return cls(
            sender=data.get(DHydraMsg.SENDER),
            target=data.get(DHydraMsg.TARGET),
            method=data.get(DHydraMsg.METHOD),
            payload=data.get(DHydraMsg.PAYLOAD),
            msg_id=data.get(DHydraMsg.ID),
        )

    @classmethod
    def from_json(cls, raw: str) -> "HydraMsg":
        return cls.from_dict(json.loads(raw))

    def sender(self, sender=None):
        if sender is not None:
            self._sender = sender
        return self._sender

    def target(self, target=None):
        if target is not None:
            self._target = target
        return self._target

    def to_dict(self) -> Dict[str, Any]:
        return {
            DHydraMsg.ID: self._id,
            DHydraMsg.SENDER: self._sender,
            DHydraMsg.TARGET: self._target,
            DHydraMsg.METHOD: self._method,
            DHydraMsg.PAYLOAD: self._payload,
            DHydraMsg.V: DHydra.PROTOCOL_VERSION,
        }

    def method(self, method=None):
        if method is not None:
            self._method = method
        return self._method

    def payload(self, payload=None):
        if payload is not None:
            self._payload = payload
        return self._payload
