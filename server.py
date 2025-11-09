from random import randint

from textual import events, work
from textual.app import App, ComposeResult
from textual.events import Print
from textual.screen import Screen, ModalScreen
from textual.widgets import Label, Button, RichLog, Footer, Placeholder, Static
from textual.containers import Grid, Horizontal, Container
from asyncio import sleep
import socket

# async def on_input_changed(self, message: Input.Changed) -> None:
#     """Called when the input changes"""
#     # update_weather us a method defined by me
#     self.run_worker(self.update_weather(message.value), exclusive=True)
# """Sau adaug inainte de metoda  decoratorul   @work(exclusive=True)
#     la metoda update_weather
# """

HOST = "127.0.0.1"
PORT = 2048

class StartServer(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Result will appear here", id="result")

    def on_mount(self) -> None:
        placeholder = self.query_one("#result",Static)
        self.receive_message(placeholder)


    @work(thread=True)
    async def receive_message(self, placeholder: Static):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((HOST, PORT))
            self.call_later(placeholder.update, f"✅ Listening on {HOST}:{PORT}")
            try:
                data, addr = s.recvfrom(1024)
                msg = data.decode("ascii")
                self.call_later(
                    placeholder.update,
                    f"📩 Message from {addr[0]}:{addr[1]} → {msg}"
                )
                Print(f"Am receptionat: {data.decode("ascii")} de la {addr}")
            except  Exception as e:
                self.call_later(placeholder.update, f"Error: {e}")


class Start(Screen):
    CSS_PATH = "Start.tcss"

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Button("Start", id="start", variant="success"),
            Button("Settings", id="settings", variant="warning"),
            Button("Quit", id="quit", variant="error"),
            id = "buttons",
        )
        yield Footer()


    def action_request_quit(self) -> None:
        self.app.exit()


class Settings(Screen):
    def compose(self):
        yield Button("Yes", id="yes", variant="primary")
        yield Footer()

    # def

class ServerGUI(App):
    BINDINGS = [
        ("s", "switch_mode('start_server')", "Start Server"),
        ("t", "switch_mode('settings')", "Settings"),
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


