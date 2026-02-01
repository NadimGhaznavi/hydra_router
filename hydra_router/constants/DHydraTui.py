class DLabel:
    CLIENT_TITLE: str = "Hydra Client"
    CONNECTED: str = "Connected"
    CONFIG: str = "Configuration"
    DISCONNECTED: str = "Disconnected"
    LISTEN_PORT: str = "Listening Port"
    PING: str = "Ping"
    ROUTER_TITLE: str = "Hydra Router"
    SERVER_TITLE: str = "Hydra Server"
    START: str = "Start"
    STATUS: str = "Status"
    TARGET_HOST: str = "Target Host"
    TARGET_PORT: str = "Target Port"
    VERSION: str = "Version"

class DStatus:
    GOOD: str = "🟢"
    BAD: str = "🔴"


class DField:
    CONFIG: str = "config"
    CONNECTED: str = "connected"
    CONSOLE: str = "console"
    STATUS: str = "status"
    TITLE: str = "title"

class DFile:
    CLIENT_CSS_PATH = "HydraClient.tcss"
    ROUTER_CSS_PATH = "HydraRouter.tcss"
