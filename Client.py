from threading import Thread

from textual import on, work
from textual.app import App, ComposeResult
from textual.widgets import Footer, Button

from Constant import Constant
from CustomModalScreens import RemoteTreeScreen, SettingsScreen
from Message import Message, PacketType
from Receiver import Receiver
from ReconstructFile import reconstruct_string, reconstruct_file
from Sender import Sender
from DivideFile import divide_file
from functools import wraps


class Client(Thread):
    window_str = "window_size(int)="
    timeout_str = "timeout(float)="
    sender_recv = ("127.0.0.1", 5000)
    sender_send = ("127.0.0.1", 6000)
    receiver_recv = ("127.0.0.1", 7000)
    receiver_send = ("127.0.0.1", 8000)


    def __init__(self):
        super().__init__()

        self.__sender = Sender(Client.sender_recv, Client.sender_send)
        self.__receiver = Receiver(Client.receiver_recv, Client.receiver_send)
        self.__content: list[Message] = []
        self.__content_index = 0

    @staticmethod
    def __show_menu() -> str:
        print("Select your command: ")
        print("00: Upload")
        print("01: Download")
        print("02: Delete")
        print("03: Move")
        print("04: Slinding Window Settings")
        resp: str = input()
        return resp

    def __append_message(self, tip: PacketType, data: str = ""):
        self.__content.append(Message(tip,  self.__content_index, data))
        self.__content_index += 1

    def __main_loop(self):
        while True:
            resp: str = self.__show_menu()
            self.__content.clear()
            self.__append_message(PacketType(resp))

            match PacketType(resp):
                case PacketType.UPLOAD:
                    # get file hierarchy
                    file_name: str = input("FileName(relative_to_root_path) =  ")
                    self.__append_message(PacketType.DATA, file_name)
                    self.__sender.start()
                    file_content = divide_file(file_name)
                    for i in range(len(file_content)):
                        self.__append_message(file_content[i])
                    self.__sender.set_content(self.__content)
                    self.__sender.start()

                case PacketType.DOWNLOAD:
                    # get file hierarchy
                    file_name: str = input("FileName(relative_to_root_path) =  ")
                    self.__append_message(PacketType.DATA, file_name)
                    self.__sender.set_content(self.__content)
                    self.__sender.start()
                    self.__receiver.start()
                    file_content = reconstruct_string(self.__receiver.delivered)
                    reconstruct_file(file_content, file_name)

                case PacketType.DELETE:
                    # get file hierarchy
                    file_name: str = input("FileName(relative_to_root_path) =  ")
                    self.__append_message(PacketType.DATA, file_name)
                    self.__sender.set_content(self.__content)
                    self.__sender.start()

                case PacketType.MOVE:
                    # get file hierarchy
                    src: str = input("src(relative_to_root_path) =  ")
                    dst: str = input("dst(relative_to_root_path) =  ")
                    self.__append_message(PacketType.DATA, src)
                    self.__append_message(PacketType.DATA, dst)
                    self.__sender.set_content(self.__content)
                    self.__sender.start()

                case PacketType.HIERARCHY:
                    self.__sender.start()                               # trimit request
                    self.__receiver.start()                             # receptionez structura folderului
                    print(self.__receiver.delivered)                    # afisez structura


                case PacketType.SETTINGS:
                    window_size = 0
                    timeout = 0.0
                    while True:
                        try:
                            window_size = int(input(Client.window_str))
                            timeout = float(input(Client.timeout_str))
                            if window_size > 0 and timeout > 0.0:
                                break
                        except ValueError: # when int() or float() fails
                            continue
                    # change the settings internally
                    self.__sender.set_timeout(timeout)
                    self.__sender.set_window_size(window_size)
                    self.__receiver.set_window_size(window_size)
                    # change the settings externally (server)
                    self.__append_message(PacketType.DATA, Constant.WINDOW_STR.value + str(window_size))
                    self.__append_message(PacketType.DATA, Constant.TIMEOUT_STR.value + str(timeout))
                    self.__sender.set_content(self.__content)
                    self.__sender.start()

    def run(self):
        self.__main_loop()

# def main():
#     client = Client()
#     client.start()
#     client.join()
#
#
# if __name__ == "__main__":
#     main()


def auto_clear(func):
    # Clears self.__content
    @wraps(func) # Preserves the original function name
    def wrapper(self, *args, **kwargs):
        if hasattr(self, "__content"):
            self.__content.clear()

        return func(self, *args, **kwargs)

    return wrapper



class ClientGUI(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]
    sender_recv = ("127.0.0.1", 5000)
    sender_send = ("127.0.0.1", 6000)
    receiver_recv = ("127.0.0.1", 7000)
    receiver_send = ("127.0.0.1", 8000)

    def __init__(self):
        super().__init__()

        self.__sender = Sender(Client.sender_recv, Client.sender_send)
        self.__receiver = Receiver(Client.receiver_recv, Client.receiver_send)
        self.__content: list[Message] = []
        self.__content_index = 0
        self.__folder_structure = None

    def __append_message(self, tip: PacketType, data: str = ""):
        self.__content.append(Message(tip,  self.__content_index, data))
        self.__content_index += 1

    def compose(self) -> ComposeResult:
        yield Button("Get Hierarchy", id='get_hierarchy')
        yield Button("Upload", id='upload')
        yield Button("Download", id='download')
        yield Button("Move", id='move')
        yield Button("Delete", id='delete')
        yield Button("Settings", id='settings')
        yield Footer()


    @auto_clear
    @work
    @on(Button.Pressed, "#get_hierarchy")
    async def handle_get_hierarchy(self):
        self.log("-"*100)
        self.log("show_folders button pressed")
        self.log("-"*100)
        self.__append_message(PacketType.HIERARCHY)
        self.__sender.start()
        # receive folder structure
        self.__receiver.start()
        self.__folder_structure = reconstruct_string(self.__receiver.delivered)

        # file_path = await self.push_screen_wait(RemoteTreeScreen(folder_structure))
        # self.log(f"From show_folders I got this={file_path}")


    # See this link for more details about push_screen_wait :)
    # https://textual.textualize.io/guide/screens/#waiting-for-screens
    @auto_clear
    @work
    @on(Button.Pressed, "#upload")
    async def handle_upload(self):
        self.log("-"*100)
        self.log("upload button pressed")
        self.log("-"*100)
        file_path = await self.push_screen_wait(RemoteTreeScreen(self.__folder_structure))

        self.__append_message(PacketType.UPLOAD)
        self.__append_message(PacketType.DATA, file_path)
        self.__sender.start()
        file_content = divide_file(file_path)
        for i in range(len(file_content)):
            self.__append_message(file_content[i])
        self.__sender.set_content(self.__content)
        self.__sender.start()


    @auto_clear
    @work
    @on(Button.Pressed, "#download")
    async def handle_download(self):
        self.log("-"*100)
        self.log("download button pressed")
        self.log("-"*100)
        file_path = await self.push_screen_wait(RemoteTreeScreen(self.__folder_structure))

        self.__append_message(PacketType.DOWNLOAD)
        self.__append_message(PacketType.DATA, file_path)
        self.__sender.set_content(self.__content)
        self.__sender.start()
        self.__receiver.start()
        file_content = reconstruct_string(self.__receiver.delivered)
        reconstruct_file(file_content, file_path)


    # @auto_clear
    # @work
    # @on(Button.Pressed, "#move")
    # async def handle_move(self):
    #     self.log("-"*100)
    #     self.log("move button pressed")
    #     self.log("-"*100)
    #
    #     src: str = input("src(relative_to_root_path) =  ")
    #     dst: str = input("dst(relative_to_root_path) =  ")
    #     self.__append_message(PacketType.MOVE)
    #     self.__append_message(PacketType.DATA, src)
    #     self.__append_message(PacketType.DATA, dst)
    #     self.__sender.set_content(self.__content)
    #     self.__sender.start()


    @auto_clear
    @work
    @on(Button.Pressed, "#delete")
    async def handle_delete(self):
        self.log("-"*100)
        self.log("delete button pressed")
        self.log("-"*100)
        file_path = await self.push_screen_wait(RemoteTreeScreen(self.__folder_structure))

        self.__append_message(PacketType.DELETE)
        self.__append_message(PacketType.DATA, file_path)
        self.__sender.set_content(self.__content)
        self.__sender.start()


    @auto_clear
    @work
    @on(Button.Pressed, "#settings")
    async def handle_settings(self):
        window_size, timeout = await self.push_screen_wait(SettingsScreen())
        self.log(f"w={window_size}, t={timeout}")
        # change the settings internally
        self.__sender.set_timeout(timeout)
        self.__sender.set_window_size(window_size)
        self.__receiver.set_window_size(window_size)
        # change the settings externally (server)
        self.__append_message(PacketType.SETTINGS)
        self.__append_message(PacketType.DATA, Constant.WINDOW_STR.value + str(window_size))
        self.__append_message(PacketType.DATA, Constant.TIMEOUT_STR.value + str(timeout))
        self.__sender.set_content(self.__content)
        self.__sender.start()


    def action_toggle_dark(self):
        """Called when the 'toggle dark' button is pressed."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
        self.log("-"*100)
        self.log("toggle_dark button pressed")
        self.log("-"*100)


    def action_quit(self):
        """Called when the quit button is pressed."""
        self.log("-"*100)
        self.log("quit button pressed")
        self.log("-"*100)
        self.exit()


if __name__ == "__main__":
    app = ClientGUI()
    app.run()