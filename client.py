from textual.app import ComposeResult, App
from textual.screen import Screen
from textual import work
from textual.widgets import Button, Input
import socket

HOST = "127.0.0.1"
PORT = 2048

class Send(Screen):
    def compose(self) -> ComposeResult:
        yield Button("Send", variant="primary", id="send")
        yield Input()


    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "send":
            self.send_message(self.query_one(Input).value)

    @work(thread=True)
    async def send_message(self, data):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.sendto(bytes(data, encoding="ascii"), (HOST, PORT))
        finally:
            s.close()


class ClientGUI(App):

    def action_request_quit(self) -> None:
        self.exit()

    def on_mount(self):
        self.push_screen(Send())

def main():
    ClientGUI().run()




if __name__ == "__main__":
    main()