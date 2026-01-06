# hydra_router/utils/HydraMsg.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

import uuid
from typing import Optional


class HydraMsg:
    def __init__(
        self,
        sender: Optional[str] = None,
        target: Optional[str] = None,
        method: Optional[str] = None,
        payload: Optional[str] = None,
    ):
        self._sender = sender
        self._target = target
        self._method = method
        self._payload = payload

        self._id = uuid.uuid4()
