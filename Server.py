
import shutil
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Vertical, Container, Horizontal
from textual.widgets import Header, Button, Footer, Log

from DivideFile import divide_file
from Message import PacketType
from Receiver import Receiver
from ReconstructFile import reconstruct_string
from Sender import Sender
from JsonFile import *
from CustomModalScreens import SettingsScreen
import threading

class Server:
    sender_recv = ("127.0.0.1", 8000)
    sender_send = ("127.0.0.1", 7000)
    receiver_recv = ("127.0.0.1", 6000)
    receiver_send = ("127.0.0.1", 5000)

    def __init__(self,app_log_callback,packet_log_callback):
        self.packet_log = packet_log_callback
        self.__receiver: Receiver = Receiver(Server.receiver_recv, Server.receiver_send,self.packet_log)
        self.__sender = Sender(Server.sender_recv, Server.sender_send,self.packet_log)
        self.__message = []
        self.app_log = app_log_callback
        self.running = False

    def update_settings(self,window_size,timeout):
        self.__sender.set_window_size(window_size)
        self.__sender.set_timeout(timeout)
        self.__receiver.set_window_size(window_size)
        self.app_log(f"Settings updated: WindowSize={window_size}, Timeout={timeout}")

    def process_message(self):
        if not self.__message:
            return
        msg = self.__message.pop(0)
        operation = msg.packet_type

        if operation == PacketType.DELETE: # 1. [ ] 2.[path]
            self.app_log("Command received -> [DELETE]")
            file_path = reconstruct_string(self.__receiver.get_ordered_packets())
            if os.path.exists(file_path):
                os.remove(file_path)
                self.app_log(f"Deleted file: {file_path}")
            else:
                self.app_log(f"File not found for deletion: {file_path}")

        elif operation == PacketType.DOWNLOAD: #  1.[ ]  [path1] [path2] ...
            self.app_log("Command received -> [DOWNLOAD]")
            src = reconstruct_string(self.__receiver.get_ordered_packets())
            self.app_log(f"Download request for : {src}")
            if os.path.exists(src):
                data_list = divide_file(Path(src))
                packet_list = [Message(PacketType.DATA, i, data_list[i]) for i in range(len(data_list))]

            else:
                self.app_log("File does not exist")
                packet_list = [Message(PacketType.DATA, 0,"!!! NO PROVIDED DATA !!!")]

            self.__sender.set_content(packet_list)
            self.__sender.start()

        elif operation == PacketType.MOVE: # 1.[ ] [source_file_name1] [source_file_name2]....  [destination_path1] [destination_path2] ...
            self.app_log("Command received -> [MOVE]")
            src = reconstruct_string(self.__receiver.get_ordered_packets())
            self.__receiver.start()
            dst = reconstruct_string(self.__receiver.get_ordered_packets())

            self.app_log(f"Moving {src} to {dst}")
            if os.path.exists(src) and os.path.exists(dst):
                shutil.move(src, dst)
                self.app_log("-> Move success")
            else:
                self.app_log("Source or Destination does not exist")

        elif operation == PacketType.UPLOAD:   # 1.[ ]  [dst1] [dst2] ...
            self.app_log("Command received -> [UPLOAD]")
            # receive file_name
            destination = reconstruct_string(self.__receiver.get_ordered_packets())
            self.app_log(f"Receiving upload to: {destination}")
            #  0-N. [data]
            self.__receiver.start()
            # pachete de tip data mai departe
            file_content = reconstruct_string(self.__receiver.get_ordered_packets())
            with open(destination, "w") as destination_file:
                destination_file.write(file_content)
            self.app_log("-> Upload complete")

        elif operation == PacketType.HIERARCHY:  #1. []
            self.app_log("Command received -> [HIERARCHY]")
            self.app_log("Sending Hierarchy...")
            folder: dict = folder_to_dict("FileExplorerServer")
            json_packets: list[Message] = divide_json(folder)

            self.__sender.set_content(json_packets)
            self.__sender.start()

        elif operation == PacketType.SETTINGS: #1.[] 2.[window_size] 3.[timeout]
            self.app_log("Command received -> [SETTINGS]")
            msg2 = self.__message.pop(0)
            msg3 = self.__message.pop(0)
            window_size = int(msg2.data)
            timeout = float(msg3.data)
            self.update_settings(window_size, timeout)

    def run(self):
        self.__receiver.start()  # blocant
        self.__message = self.__receiver.get_ordered_packets()

        if self.__message:
            # self.app_log("Command received ...")
            self.__sender = Sender(Server.sender_recv, Server.sender_send,self.packet_log)
            try:
                self.process_message()
            except Exception as e:
                self.app_log(f"Error : {e}")
                self.packet_log(f"Exception: {e}")

        # self.app_log("Job done. Waiting for next command...")
        self.__message = []
    
    def stop(self):
        self.running = False
        if self.__receiver:
            self.__receiver.stop()
        if self.__sender:
            self.__sender.stop()


class ServerGUI(App):
    CSS = """
        Screen {
            layout: vertical;
        }
        #control_panel {
            height: 3;
            dock: top;
            align: center middle;
            background: $panel;
            border-bottom: solid $primary;
        }
        #main_area {
            layout: horizontal;
            height: 1fr;
        }
        .column {
            width: 1fr;
            height: 100%;
            border: solid $secondary;
            margin: 0 1;
        }
        #app_log {
            background: $surface;
            color: $text;
            border: solid green;
        }
        #packet_log {
            background: $surface-darken-1;
            color: green;
        }
        Button {
            margin: 0 1;
        }
        Label {
            text-align: center;
            width: 100%;
            background: $primary;
            color: white;
        }
        """

    def __init__(self):
        super().__init__()
        self.server_app_logic = Server(self.write_to_terminal,self.write_packet_log)
        self.server_is_running = False
        
    def compose(self)-> ComposeResult:
        yield Header()

        with Container(id="control_panel"):
            with Horizontal(id="buttons"):
                yield Button("Start Server", id="start", variant="success")
                yield Button("Stop Server", id="stop", variant="error", disabled=True)
                yield Button("Settings", id="settings", variant="primary")

        with Horizontal(id="main_area"):
            with Vertical(classes="column"):
                log_app = Log(id="app_log", highlight=True)
                log_app.border_title = "Main Operations"
                yield log_app

            with Vertical(classes="column"):
                log_packet = Log(id="packet_log", highlight=True)
                log_packet.border_title = "Packet Traffic / ACKs"
                yield log_packet

        yield Footer()

    def on_mount(self):
        self.write_to_terminal("Press 'Start' to listen")
        self.write_packet_log("Waiting for traffic...")
    
    def write_to_terminal(self,text:str):
        self.query_one("#app_log", Log).write_line(text)

    def write_packet_log(self,text:str):
        log = self.query_one("#packet_log", Log)

        if threading.get_ident() == self._thread_id:
            log.write_line(text)
        else:
            self.call_from_thread(log.write_line,text)


    @on(Button.Pressed, "#start")
    def action_start_server(self):
        if not self.server_is_running:
            self.server_is_running = True
            self.server_app_logic.running = True

            self.query_one("#start").disabled = True
            self.query_one("#stop").disabled = False
            self.query_one("#settings").disabled = True

            self.write_to_terminal("\tServer STARTED")
            self.run_server_worker()

    @on(Button.Pressed, "#stop")
    def action_stop_server(self):
        if self.server_is_running:
            self.server_is_running = False
            self.server_app_logic.stop()

            self.query_one("#start").disabled = False
            self.query_one("#stop").disabled = True
            self.query_one("#settings").disabled = False

            self.write_to_terminal("\tServer STOPPED")

    @work(thread=True)
    def run_server_worker(self):
        while self.server_is_running:
            try:
                self.server_app_logic.run()
            except Exception as e:
                self.call_from_thread(self.write_to_terminal, f"Critical Error in loop: {e}")
                break
        # self.call_from_thread(self.write_to_terminal, "Server loop terminated.")

    @work
    @on(Button.Pressed, "#settings")
    async def handle_settings(self):
        self.write_to_terminal("Opening settings...")
        window_size, timeout = await self.push_screen_wait(SettingsScreen())

        if window_size > 0 and timeout > 0.0:
            self.server_app_logic.update_settings(window_size, timeout)
            self.write_to_terminal(f"Settings Applied: WindowSize={window_size}, Timeout={timeout}")
        else:
            self.write_to_terminal("Settings cancelled.")

    
def main():

    # server = ServerDeprecated()
    # server.start()
    # try:
    #     while True:
    #         pass
    # except KeyboardInterrupt:
    #     print("Server stopped")
    #     server.stop()

    app = ServerGUI()
    app.run()

if __name__ == "__main__":
    main()