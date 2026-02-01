import sys
import zmq
import asyncio
import zmq.asyncio

from textual.theme import Theme
from textual.app import App, ComposeResult
from textual.widgets import Label, Button, Log
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive

from hydra_router.utils.HydraMQ import HydraMQ
from hydra_router.utils.HydraMsg import HydraMsg
from hydra_router.constants.DHydra import DHydra, DHydraRouter, DModule, DMethod
from hydra_router.constants.DHydraTui import DLabel, DField, DFile, DStatus



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


class HydraClientTui(App):
    """A Textual interface to the HydraServer"""

    TITLE = DLabel.CLIENT_TITLE
    CSS_PATH = DFile.CLIENT_CSS_PATH

    def __init__(self, address: str = DHydraRouter.HOSTNAME, port: int = DHydraRouter.PORT) -> None:
        """Constructor"""
        super().__init__()


        self._address = address
        self._port = port
        self._id = str = DModule.HYDRA_CLIENT
        self._connected_msg = DStatus.BAD + " " + DLabel.DISCONNECTED
        self.mq = None
        self.check_connection_stop_event = asyncio.Event()

    def compose(self) -> ComposeResult:
        """The TUI is created here"""

        # Title
        yield Label(DLabel.CLIENT_TITLE, id=DField.TITLE)

        # Configuration
        yield Vertical(
            Label(f"{DLabel.TARGET_HOST}: {self._address}"),
            Label(f"{DLabel.TARGET_PORT}: {self._port}"),
            id=DField.CONFIG
        )

        # Runtime status
        yield Vertical(
            Label(f"{self._connected_msg}", id=DField.CONNECTED),
            id=DField.STATUS
        )

        # Console
        yield Log(highlight=True, auto_scroll=True, id=DField.CONSOLE)

        # Buttons
        yield Horizontal(
            Button(label=DLabel.PING, id=DMethod.PING, compact=True),
            Label(" "),
            Button(label="Quit", id="quit", compact=True),
            id="buttons"
        )

    async def check_connection(self) -> None:
        while not self.check_connection_stop_event.is_set():
            if self.mq.connected():
                self._connected_msg = DStatus.GOOD + " " + DLabel.CONNECTED
            else:
                self._connected_msg = DStatus.BAD + " " + DLabel.DISCONNECTED

            self.query_one(f"#{DField.CONNECTED}", Label).update(self._connected_msg)
            
            await asyncio.sleep(DHydra.HEARTBEAT_INTERVAL + 1)


    def console_msg(self, msg: str):
        self.query_one(Log).write_line(msg)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == DMethod.PING:
            msg = HydraMsg(sender=DModule.HYDRA_CLIENT, target=DModule.HYDRA_ROUTER, method=DMethod.PING)            
            self.console_msg("Sending ping")
            await self.mq.send(msg)
            reply = await self.mq.recv()
            if reply.method == DMethod.PONG:
                self.console_msg("Received pong")

        elif button_id == "quit":
            await self.on_quit()
            
    def on_mount(self):
        self.mq = HydraMQ(router_address=self._address, router_port=self._port, id=self._id)
        self.mq.start_heartbeat()
        self.check_connection_task = asyncio.create_task(self.check_connection())
        self.query_one(f"#{DField.TITLE}").border_subtitle = DLabel.VERSION + " " + DHydra.VERSION
        self.query_one(f"#{DField.CONFIG}").border_subtitle = DLabel.CONFIG
        self.query_one(f"#{DField.STATUS}").border_subtitle = DLabel.STATUS
        self.query_one(f"#{DField.CONSOLE}", Log).write_line("Initialization complete")

    async def on_quit(self):
        await self.mq.quit()

        if self.check_connection_task is not None:
            self.check_connection_stop_event.set()
            await asyncio.sleep(0.1)
            self.check_connection_task.cancel()
            try:
                await self.check_connection_task
            except asyncio.CancelledError:
                pass

        sys.exit(0)

def main():
    router = HydraClientTui()
    router.run()


if __name__ == "__main__":
    main()
