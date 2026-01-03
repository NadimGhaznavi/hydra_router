"""
ZMQMessage - Internal message format for client applications.

This module defines the ZMQMessage class used internally by applications
that is automatically converted to/from RouterConstants format by MQClient.
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .constants.DMsgType import DMsgType


@dataclass
class ZMQMessage:
    """
    Internal message format used by client applications.

    This format is used internally by applications and is automatically
    converted to/from RouterConstants format by the MQClient.
    """

    message_type: DMsgType
    timestamp: Optional[float] = None
    client_id: Optional[str] = None
    request_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Set default timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result: Dict[str, Any] = {
            "message_type": self.message_type.value,
            "timestamp": self.timestamp,
        }

        if self.client_id is not None:
            result["client_id"] = self.client_id
        if self.request_id is not None:
            result["request_id"] = self.request_id
        if self.data is not None:
            result["data"] = self.data

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZMQMessage":
        """Create ZMQMessage from dictionary representation."""
        message_type = DMsgType(data["message_type"])

        return cls(
            message_type=message_type,
            timestamp=data.get("timestamp"),
            client_id=data.get("client_id"),
            request_id=data.get("request_id"),
            data=data.get("data"),
        )
