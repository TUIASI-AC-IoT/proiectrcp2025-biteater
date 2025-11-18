import threading
from random import randint

from textual import events, work
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.screen import Screen, ModalScreen
from textual.widgets import Label, Button, RichLog, Footer, Placeholder, Static
from textual.containers import Grid, Horizontal, Container
import socket

HOST = "127.0.0.1"
PORT_TX = 5000
PORT_RX = 6000


class StartServer(ModalScreen):
    BINDINGS = [("q", "request_quit", "quit and back to the main menu")]
    response = reactive("")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__stop_flag = threading.Event()

    def compose(self) -> ComposeResult:
        yield Button("Stop Server", id="stop")
        yield Footer()


    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "stop":
            self.__stop_flag.set()
            self.app.switch_mode("start")

    def action_request_quit(self):
        self.__stop_flag.set()
        self.app.switch_mode("start")

    @work(thread=True)
    async def receive_message(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            self.__stop_flag.clear()
            s.bind((HOST, PORT_RX))
            s.settimeout(1)
            self.app.call_from_thread(self.query_one("#result").update, f"✅ Listening on {HOST}:{PORT_RX}")
            while not self.__stop_flag.is_set():
                try:
                    data, addr = s.recvfrom(1024)
                    self.__stop_flag.set()
                    msg = data.decode("ascii")
                    self.app.call_from_thread(self.query_one("#result").update, f"Received message: {msg}")
                except socket.timeout:
                    continue



class Settings(ModalScreen):
    def compose(self):
        yield Button("Yes", id="yes", variant="primary")
        yield Footer()


class Start(ModalScreen):
    CSS_PATH = "Start.tcss"
    BINDINGS = [
        ("s", "app.switch_mode('start_server')", "Start Server"),
        ("t", "app.switch_mode('settings')", "Settings"),
        ("q", "request_quit", "Quit")
        ]

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Button("Start", id="start", variant="success"),
            Button("Settings", id="settings", variant="warning"),
            Button("Quit", id="quit", variant="error"),
            id = "buttons",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "start":
            self.app.switch_mode('start_server')
        elif event.button.id == "settings":
            self.app.switch_mode('settings')
        elif event.button.id == "quit":
            self.app.exit()

    def action_request_quit(self) -> None:
        self.app.exit()



class ServerGUI(App):
    BINDINGS = [
        ("q", "request_quit", "Quit"),
    ]
    DEFAULT_MODE = 'start'
    MODES = {
        "start" : Start,
        "start_server" : StartServer,
        "settings" : Settings,
    }

    def action_request_quit(self) -> None:
        self.exit()


def main():
    ServerGUI().run()

if __name__ == "__main__":
    main()


