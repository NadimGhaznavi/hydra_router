import zmq
import asyncio
import zmq.asyncio

from textual import work
from textual.theme import Theme
from textual.app import App, ComposeResult
from textual.widgets import Label, Button, Log
from textual.containers import Vertical, Horizontal
from textual.reactive import var

from hydra_router.utils.HydraMsg import HydraMsg
from hydra_router.constants.DHydra import DHydraServerDef, DMethod
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
    CSS_PATH = DFile.ROUTER_CSS_PATH

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

        yield Label(DLabel.ROUTER_TITLE, classes="title")
        yield Label(f"{DLabel.LISTENING}: {self._address}:{self._port}", classes="box")
        yield Log(highlight=True, auto_scroll=True, id="console")
        yield Button(label=DLabel.START, id=DMethod.START, compact=True)


    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == DMethod.START:
            self.bg_listen()

    @work(exclusive=True)
    async def bg_listen(self) -> None:
        if self.socket is None:
            self._init_socket()

        try:
            while True:
                if self.socket is not None:
                    # Receive multipart message
                    frames = await self.socket.recv_multipart()
                    
                    # frames[0] = client identity (bytes)
                    # frames[1] = message data (JSON bytes)
                    client_identity = frames[0]
                    message_data = frames[1]
                    
                    # Deserialize to HydraMsg
                    hydra_msg = HydraMsg.from_json(message_data)
                    
                    # Display in log
                    self.query_one(Log).write_line(
                        f"From: {hydra_msg.sender}, "
                        f"Method: {hydra_msg.method}, "
                        f"Target: {hydra_msg.target}"
                    )
                    
                    # Store for reactive updates if needed
                    self.raw_message = str(hydra_msg)
                else:
                    raise RuntimeError("Socket is not initialized")
                await asyncio.sleep(0.1)

        except Exception as e:
            self.query_one(Log).write_line(f"ERROR: {e}")
            exit(1)


    def watch_raw_message(self, raw_value: str):
        pass #self.query_one("#console", Log).write_line(raw_value)



def main():
    router = HydraRouterTui()
    router.run()


if __name__ == "__main__":
    main()
