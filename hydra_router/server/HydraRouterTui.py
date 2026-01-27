import sys
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
from hydra_router.constants.DHydra import DHydra, DHydraServerDef, DMethod, DModule
from hydra_router.constants.DHydraTui import DLabel, DFile, DField

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

        # Title
        yield Label(DLabel.ROUTER_TITLE, id=DField.TITLE)

        # Configuration
        yield Vertical(
            Label(f"{DLabel.LISTEN_PORT}: {self._port}"),
            id=DField.CONFIG
        )

        # Console
        yield Log(highlight=True, auto_scroll=True, id="console")

        # Buttons
        yield Horizontal(
            Button(label=DLabel.START, id=DMethod.START, compact=True),
            Label(" "),
            Button(label="Quit", id="quit", compact=True),
            id="buttons"
        )
            

    async def handle_message(self, sender: str, msg: HydraMsg) -> None:
        # Display in log
        self.query_one(Log).write_line(
            f"From: {msg.sender}, "
            f"Method: {msg.method}, "
            f"Target: {msg.target}"
        )
        
        # Create and send reply
        reply_msg = HydraMsg(
            sender=DModule.HYDRA_ROUTER,
            target=msg.sender,
            method="pong" if msg.method == DMethod.PING else "response",
            payload={"status": "received", "echo": msg.method}
        )

        # Send reply using ROUTER multipart format
        await self.socket.send_multipart([
            sender,
            reply_msg.to_json()
        ])

        self.query_one(Log).write_line(f"Sent reply to {msg.sender} (id: {reply_msg.id})")



    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == DMethod.START:
            self.bg_listen()

        elif button_id == "quit":
            await self.on_quit()

    def on_mount(self):
        self.query_one(f"#{DField.TITLE}").border_subtitle = DLabel.VERSION + " " + DHydra.VERSION
        self.query_one(f"#{DField.CONFIG}").border_subtitle = DLabel.CONFIG

    async def on_quit(self):
        sys.exit(0)

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
                    sender = frames[0]
                    message_data = frames[1]
                    
                    # Deserialize to HydraMsg
                    hydra_msg = HydraMsg.from_json(message_data)
                    
                    # Handle the message
                    await self.handle_message(sender, hydra_msg)

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
