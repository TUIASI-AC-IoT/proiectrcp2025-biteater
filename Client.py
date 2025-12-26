import re

from Message import PacketType, Message
from Receiver import Receiver
from Sender import Sender
from DivideFile import divide_file
from ReconstructFile import reconstruct_file, reconstruct_string


class Client:
    window_str = "window_size(int)="
    timeout_str = "timeout(float)="
    sender_recv = ("127.0.0.1", 5000)
    sender_send = ("127.0.0.1", 6000)
    receiver_recv = ("127.0.0.1", 7000)
    receiver_send = ("127.0.0.1", 8000)


    def __init__(self):
        self.__sender = Sender(Client.sender_recv, Client.sender_send)
        self.__receiver = Receiver(Client.receiver_recv, Client.receiver_send)
        self.__content: list[Message] = []
        self.__content_index = 0

    def __show_menu(self) -> str:
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
                    file_name: str = input("FileName(abs_path) =  ")
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

                    file_name = re.sub(r'FileExplorerServer','FileExplorerClient',file_name)
                    reconstruct_file(file_content, file_name)

                case PacketType.DELETE:
                    # get file hierarchy
                    file_name: str = input("FileName(abs_path) =  ")
                    self.__append_message(PacketType.DATA, file_name)
                    self.__sender.set_content(self.__content)
                    self.__sender.start()

                case PacketType.MOVE:
                    # get file hierarchy
                    src: str = input("src(abs_path) =  ")
                    dst: str = input("dst(abs_path) =  ")
                    self.__append_message(PacketType.DATA, src)
                    self.__append_message(PacketType.DATA, dst)
                    self.__sender.set_content(self.__content)
                    self.__sender.start()

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
                    self.__append_message(PacketType.DATA, Client.window_str + str(window_size))
                    self.__append_message(PacketType.DATA, Client.timeout_str + str(timeout))
                    self.__sender.set_content(self.__content)
                    self.__sender.start()

    def start(self):
        self.__main_loop()

def main():
    Client().start()


if __name__ == "__main__":
    main()

