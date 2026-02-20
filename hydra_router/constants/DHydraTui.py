# hydra_router/constants/DHydraTui.py
#
#    Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

from typing import Final


class DLabel:
    CLIENT_TITLE: Final[str] = "Hydra Client"
    CLIENTS: Final[str] = "Clients"
    CONNECTED: Final[str] = "Connected"
    CONFIG: Final[str] = "Configuration"
    DISCONNECTED: Final[str] = "Disconnected"
    ERROR: Final[str] = "ERROR"
    LISTEN_PORT: Final[str] = "Listening Port"
    PING: Final[str] = "Ping"
    PING_ROUTER: Final[str] = "Ping Router"
    PING_SERVER: Final[str] = "Ping Server"
    QUIT: Final[str] = "Quit"
    ROUTER_TITLE: Final[str] = "Hydra Router"
    SERVER_TITLE: Final[str] = "Hydra Server"
    SPACE: Final[str] = " "
    START: Final[str] = "Start"
    STATUS: Final[str] = "Status"
    TARGET_HOST: Final[str] = "Target Host"
    TARGET_PORT: Final[str] = "Target Port"
    VERSION: Final[str] = "Version"


class DStatus:
    GOOD: Final[str] = "🟢"
    OK: Final[str] = "🟡"
    BAD: Final[str] = "🔴"


class DField:
    BUTTONS: Final[str] = "buttons"
    CLIENTS: Final[str] = "clients"
    CLIENTS_SCREEN: Final[str] = "clients_screen"
    CONFIG: Final[str] = "config"
    CONNECTED: Final[str] = "connected"
    CONSOLE: Final[str] = "console"
    CONSOLE_SCREEN: Final[str] = "console_screen"
    QUIT: Final[str] = "quit"
    RUNNING: Final[str] = "running"
    STATUS: Final[str] = "status"
    STOPPED: Final[str] = "stopped"
    TITLE: Final[str] = "title"


class DFile:
    CLIENT_CSS_PATH: Final[str] = "HydraClient.tcss"
    ROUTER_CSS_PATH: Final[str] = "HydraRouter.tcss"
