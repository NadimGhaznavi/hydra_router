import zmq
import asyncio
import zmq.asyncio

from textual.theme import Theme
from textual.app import App, ComposeResult
from textual.widgets import Label, Button, Log
from textual.containers import Vertical, Horizontal
from textual.reactive import var

from hydra_router.constants.DHydra import DHydraServerDef
from hydra_router.constants.DHydraTui import DLabel, DFile

HYDRA_THEME = Theme(
    name="hydra_theme",
    primary="#88C0D0",
    secondary="#1f6a83ff",
    accent="#B48EAD",
    foreground="#31b8e6",
    background="black",
    success="#A3BE8C",
    warning="#EBCB8B",
    error="#BF616A",
    surface="#111111",
    panel="#000000",
    dark=True,
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#88C0D0",
        "input-selection-background": "#81a1c1 35%",
    },
)


class HydraRouterTui(App):
    """A Textual interface to the HydraServer"""

    TITLE = DLabel.ROUTER_TITLE
    CSS_PATH = DFile.CSS_PATH

    raw_message = var("")

    def __init__(self, address: str = "*", port: int = DHydraServerDef.PORT) -> None:
        """Constructor"""
        super().__init__()

        self._address = address
        self._port = port
        self._listening = False
        self.socket = None
        self._init_socket()

    def _init_socket(self) -> None:
        try:
            bind_address = f"tcp://{self._address}:{self._port}"
            self.context = zmq.asyncio.Context()
            self.socket = self.context.socket(zmq.ROUTER)
            self.socket.bind(bind_address)
        except Exception as e:
            print(f"ERROR: {e}")
            exit(1)

    def compose(self) -> ComposeResult:
        """The TUI is created here"""

        yield Vertical(
            Label(DLabel.SERVER_TITLE, classes="title"),
            Label(f"Address: {self._address}:{self._port}"),
            Log(highlight=True, auto_scroll=True, id="console"),
            classes="box",
        )

    def listen(self) -> None:
        self.listen_task = asyncio.create_task(self.bg_listen())


    async def bg_listen(self) -> None:
        if self.socket is None:
            self._init_socket()

        try:
            while True:
                if self.socket is not None:
                    self.raw_message = self.socket.recv()
                    # self.socket.send(response)
                else:
                    raise RuntimeError("Socket is not initialized")
                asyncio.sleep(0.1)

        except Exception as e:
            self.raw_message = f"ERROR: {e}"
            exit(1)

    def watch_raw_message(self, raw_value: str):
        pass #self.query_one("#console", Log).write_line(raw_value)



def main():
    router = HydraRouterTui()
    router.run()


if __name__ == "__main__":
    main()
