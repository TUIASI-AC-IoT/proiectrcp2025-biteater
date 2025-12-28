import asyncio

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Center, CenterMiddle
from textual.widgets import Footer, Button

from Constant import Constant
from CustomModalScreens import RemoteTreeScreen, SettingsScreen, MoveScreen
from JsonFile import folder_to_dict
from Message import Message, PacketType
from Receiver import Receiver
from ReconstructFile import reconstruct_string, reconstruct_file
from Sender import Sender
from DivideFile import divide_file
import json

def get_client_folder() -> dict:
    return folder_to_dict(str(Constant.CLIENT_FOLDER_PATH.value))



class ClientGUI(App):
    CSS_PATH = "./css/Client.tcss"
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "stop_operation", "Stop Operations")
    ]
    sender_recv = ("127.0.0.1", 5000)
    sender_send = ("127.0.0.1", 6000)
    receiver_recv = ("127.0.0.1", 7000)
    receiver_send = ("127.0.0.1", 8000)
    server_exists = True               # for debug purposes while server is off

    def __init__(self):
        super().__init__()

        self.__sender = Sender(ClientGUI.sender_recv, ClientGUI.sender_send)
        self.__receiver = Receiver(ClientGUI.receiver_recv, ClientGUI.receiver_send)
        self.__content: list[Message] = []
        self.__content_index = 0
        self.__folder_structure_server: dict | None = None
        self.__stop_all = False                 # when user press "s" we want to stop everything
                                                # and not create any thread using asyncio.to_thread()
                                                # we need this flag only for the second call of asyncio.to_thread()

    def __append_message(self, tip: PacketType, data: str = ""):
        self.__content.append(Message(tip,  self.__content_index, data))
        self.__content_index += 1


    def on_mount(self):
        self.theme = "tokyo-night"

    def compose(self) -> ComposeResult:
        with CenterMiddle():
            yield Button("Upload", id='upload')
            yield Button("Download", id='download')
            yield Button("Move", id='move')
            yield Button("Delete", id='delete')
            yield Button("Settings", id='settings')
        yield Footer()


    def __reset_content(self):
        self.__content.clear()
        self.__content_index = 0


    def handle_get_hierarchy(self):
        self.__reset_content()

        if ClientGUI.server_exists:
            self.__append_message(PacketType.HIERARCHY)
            self.__sender.set_content(self.__content)

            ## Functions that runs in background
            self.__sender.start()
            # receive folder structure

            ## Functions that runs in background
            if not self.__stop_all:
                self.__receiver.start()
            else:
                # if it was true, then I reset it
                self.__stop_all = False

            # This code runs on the main thread after the receiver is done
            received_packets = self.__receiver.get_ordered_packets()

            if len(received_packets) > 0:
                try:
                    self.__folder_structure_server: dict | None = json.loads(reconstruct_string(received_packets))
                except json.JSONDecodeError as e:
                    self.log(f"Decode: {e}")
                except Exception as e:
                    self.log(f"General:\n{e}")
                else:
                    self.log(f"res=\n{self.__folder_structure_server}")



    # See this link for more details about push_screen_wait :)
    # https://textual.textualize.io/guide/screens/#waiting-for-screens
    @work
    @on(Button.Pressed, "#upload")
    async def handle_upload(self):
        self.query_one("#upload", Button).loading = True
        await asyncio.to_thread(self.handle_get_hierarchy)
        self.__reset_content()

        src, dst = await self.push_screen_wait(MoveScreen(self.__folder_structure_server, get_client_folder() ))

        if ClientGUI.server_exists:
            if src and dst:
                temp: list[str] = src.split('/')
                dst = str(Constant.SERVER_FOLDER_PATH.value) + dst + '/' + temp[len(temp) - 1]
                src = str(Constant.CLIENT_FOLDER_PATH.value) + src
                self.log(f"dst = {dst}")
                self.log(f"src = {src}")

                self.__append_message(PacketType.UPLOAD)
                self.__append_message(PacketType.DATA, dst)
                self.__sender.set_content(self.__content)

                ## Functions that runs in background
                # Announce server about our intention to upload a file
                await asyncio.to_thread(self.__sender.start)
                self.__reset_content()

                # This code runs on the main thread after
                # the sender is done

                file_content = divide_file(src)
                for i in range(len(file_content)):
                    self.__append_message(PacketType.DATA, file_content[i])
                self.__sender.set_content(self.__content)

                if not self.__stop_all:
                    ## Functions that runs in background
                    self.log("REACHED SENDING")
                    await asyncio.to_thread(self.__sender.start)
                else:
                    # if it was true, then I reset it
                    self.__stop_all = False

        self.query_one("#upload", Button).loading = False


    @work
    @on(Button.Pressed, "#download")
    async def handle_download(self):
        self.query_one("#download", Button).loading = True
        await asyncio.to_thread(self.handle_get_hierarchy)
        self.__reset_content()

        src, dst = await self.push_screen_wait(MoveScreen(get_client_folder(), self.__folder_structure_server))

        if ClientGUI.server_exists:
            if src and dst:
                src = str(Constant.SERVER_FOLDER_PATH.value) + src
                temp: list[str] = src.split('/')
                dst = str(Constant.CLIENT_FOLDER_PATH.value) + dst + '/' + temp[len(temp) - 1]

                self.__append_message(PacketType.DOWNLOAD)
                self.__append_message(PacketType.DATA, src)
                self.__sender.set_content(self.__content)

                ## Functions that runs in background
                # Announce server about our intention to download a file
                await asyncio.to_thread(self.__sender.start)

                if not self.__stop_all:
                    ## Functions that runs in background
                    await asyncio.to_thread(self.__receiver.start)
                else:
                    # if it was true, then I reset it
                    self.__stop_all = False

                file_content: str = reconstruct_string(self.__receiver.get_ordered_packets())
                if file_content == '' or file_content == Constant.NO_DATA.value:
                    self.notify("Failed to download a file", title="DOWNLOAD OPERATION", severity="error")
                else:
                    reconstruct_file(file_content, dst)

        self.query_one("#download", Button).loading = False


    @work
    @on(Button.Pressed, "#move")
    async def handle_move(self):
        self.query_one("#move", Button).loading = True
        await asyncio.to_thread(self.handle_get_hierarchy)
        self.__reset_content()

        src, dst = await self.push_screen_wait(MoveScreen(self.__folder_structure_server))


        if ClientGUI.server_exists:
            if src and dst:
                src = str(Constant.SERVER_FOLDER_PATH.value) + src
                dst = str(Constant.SERVER_FOLDER_PATH.value) + dst

                self.__append_message(PacketType.MOVE)
                self.__append_message(PacketType.DATA, src)
                self.__append_message(PacketType.DATA, dst)
                self.__sender.set_content(self.__content)

                ## Functions that runs in background so app GUI can be refreshed
                await asyncio.to_thread(self.__sender.start)
        self.query_one("#move", Button).loading = False


    @work
    @on(Button.Pressed, "#delete")
    async def handle_delete(self):
        self.query_one("#delete", Button).loading = True
        await asyncio.to_thread(self.handle_get_hierarchy)
        self.__reset_content()

        file_path = await self.push_screen_wait(RemoteTreeScreen("Delete", self.__folder_structure_server, True))

        if ClientGUI.server_exists:
            if file_path:
                file_path = str(Constant.SERVER_FOLDER_PATH.value) + file_path

                self.__append_message(PacketType.DELETE)
                self.__append_message(PacketType.DATA, file_path)
                self.__sender.set_content(self.__content)

                ## Functions that runs in background
                await asyncio.to_thread(self.__sender.start)
        self.query_one("#delete", Button).loading = False


    @work
    @on(Button.Pressed, "#settings")
    async def handle_settings(self):
        self.query_one("#settings", Button).loading = True
        self.__reset_content()

        window_size, timeout = await self.push_screen_wait(SettingsScreen())
        self.log(f"w={window_size}, t={timeout}")
        if window_size > 0 and timeout > 0.0:
            # change the settings internally
            self.__sender.set_timeout(timeout)
            self.__sender.set_window_size(window_size)
            self.__receiver.set_window_size(window_size)
            # change the settings externally (server)

            if ClientGUI.server_exists:
                    self.__append_message(PacketType.SETTINGS)
                    self.__append_message(PacketType.DATA, str(window_size))
                    self.__append_message(PacketType.DATA, str(timeout))
                    self.__sender.set_content(self.__content)

                    ## Functions that runs in background
                    await asyncio.to_thread(self.__sender.start)
        self.query_one("#settings", Button).loading = False


    def action_stop_operation(self):
        """Called when the stop operation button is pressed."""
        self.__sender.stop()
        self.__receiver.stop()
        self.__stop_all = True


    def action_quit(self):
        """Called when the quit button is pressed."""
        self.__sender.stop()
        self.__receiver.stop()
        self.exit()


if __name__ == "__main__":
    app = ClientGUI()
    app.run()