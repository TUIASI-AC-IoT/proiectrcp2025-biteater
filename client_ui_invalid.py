import threading

from textual.app import ComposeResult, App
from textual.containers import Center, Vertical, Container
from textual.screen import Screen, ModalScreen
from textual import work
from textual.widgets import Button, Input
import socket

HOST = "127.0.0.1"
PORT_TX = 6000
PORT_RX = 5000

class Send(ModalScreen):
    BINDINGS = [("q", "request_quit", "Quit")]

    def __init__(self):
        super().__init__()
        self.__stop_sending = threading.Event()
        self.__stop_receiving = threading.Event()
        self.rx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rx_socket.bind((HOST, PORT_RX))
        self.rx()
        self.tx()

    CSS_PATH = "send_client.tcss"

    def compose(self) -> ComposeResult:
        with Container(id="send-box"):
            yield Button("Send", variant="primary", id="send")
            yield Input()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "send":
            self.send(self.query_one(Input).value)

    # The function is called when the user presses q button, because i setted it in bindings
    def action_request_quit(self):
        self.__stop_sending.set()
        self.__stop_receiving.set()
        self.app.exit()

    def send(self, data):
        try:
            self.tx_socket.sendto(bytes(data, encoding="ascii"), (HOST, PORT_TX))
        finally:
            self.tx_socket.close()

    def receive(self):
        try:
            data, addr = self.rx_socket.recvfrom(1024)
        finally:
            self.rx_socket.close()
        return data, addr

    @work(exclusive=True, thread=True)
    def rx(self):
        while not self.__stop_receiving.is_set():
            self.rx_socket.settimeout(1)
            try:
                data, addr = self.receive()
            except socket.timeout:
                continue


    @work(exclusive=True, thread=True)
    def tx(self):
        data = "ceva"
        while not self.__stop_sending.is_set():
            self.tx_socket.settimeout(1)
            try:
                self.send(data)
            except socket.timeout:
                continue



class ClientGUI(App):
    MODES = {
        "send" : Send,
    }
    DEFAULT_MODE = 'send'

    def on_mount(self):
        self.push_screen(Send())

def main():
    ClientGUI().run()




if __name__ == "__main__":
    main()
