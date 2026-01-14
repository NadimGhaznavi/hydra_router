import zmq
import asyncio
import zmq.asyncio

from textual.theme import Theme
from textual.app import App, ComposeResult
from textual.widgets import Label, Button, Log
from textual.containers import Vertical, Horizontal
from textual.reactive import var

from hydra_router.utils.HydraMsg import HydraMsg
from hydra_router.constants.DHydra import DHydraServerDef, DModule, DMethod
from hydra_router.constants.DHydraTui import DLabel, DField, DFile

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
    CSS_PATH = DFile.CSS_PATH

    raw_message = var("")

    def __init__(self, address: str = "*", port: int = DHydraServerDef.PORT) -> None:
        """Constructor"""
        super().__init__()

        self._address = address
        self._port = port

    def compose(self) -> ComposeResult:
        """The TUI is created here"""

        yield Vertical(
            Label(DLabel.CLIENT_TITLE, classes=DField.TITLE),
            Label(f"Address: {self._address}:{self._port}"),
            Button(label=DLabel.PING, id=DMethod.PING, compact=True),
            Log(highlight=True, auto_scroll=True, id=DField.CONSOLE),
            classes=DField.BOX,
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == DMethod.PING:
            msg = HydraMsg(sender=DModule.HYDRA_CLIENT, target=DModule.HYDRA_ROUTER, method=DMethod.PING)
            
                           



def main():
    router = HydraClientTui()
    router.run()


if __name__ == "__main__":
    main()
