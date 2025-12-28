
import shutil


from DivideFile import divide_file
from Message import PacketType
from Receiver import Receiver
from ReconstructFile import reconstruct_string
from Sender import Sender
from JsonFile import *

class Server:
    sender_recv = ("127.0.0.1", 8000)
    sender_send = ("127.0.0.1", 7000)
    receiver_recv = ("127.0.0.1", 6000)
    receiver_send = ("127.0.0.1", 5000)

    def __init__(self):
        self.__receiver: Receiver = Receiver(Server.receiver_recv, Server.receiver_send)
        self.__sender = Sender(Server.sender_recv, Server.sender_send)
        self.__message = []

    def start(self):
        #             #simulare primire mesaj
        # file_path = "FileExplorerServer/dir1/file2.txt"
        # destination_path = "FileExplorerServer/dir2"
        # self.__message.append(Message(packet_type=PacketType.MOVE,sequence=0,data=file_path))
        # self.__message.append(Message(packet_type=PacketType.DELETE,sequence=0,data=destination_path))
        #
        # #UPLOAD
        # file_path = "FileExplorerServer/dir1/file1.txt"
        # content = "HELLO WORLD"
        # destination_path = "FileExplorerServer/dir2"
        # self.__message.append(Message(packet_type=PacketType.UPLOAD,sequence=0,data=file_path))
        # self.__message.append(Message(packet_type=PacketType.DELETE,sequence=0,data=content))
        while True:
            self.__receiver.start()  #blocant
            self.__message = self.__receiver.get_ordered_packets()

            if self.__message:
                print("\tCommand received ...")
                self.__sender = Sender(Server.sender_recv, Server.sender_send)
                try:
                    self.process_message()
                except Exception as e:
                    print(e)
            print("Job done. Waiting for next command...")
            self.__message = []


    def process_message(self):
        if not self.__message:
            return
        msg = self.__message.pop(0)
        operation = msg.packet_type

        if operation == PacketType.DELETE: # 1. [ ] 2.[path]
            msg2 = self.__message.pop(0)
            file_path = msg2.data
            if os.path.exists(file_path):
                os.remove(file_path)
            else:
                print("The file does not exist")

        elif operation == PacketType.DOWNLOAD: #  1.[ ]  2. [path]
            msg2 = self.__message.pop(0)
            file_path = msg2.data
            if os.path.exists(file_path):
                data_list = divide_file(file_path)
                packet_list = [Message(PacketType.DATA, i, data_list[i]) for i in range(len(data_list))]

            else:
                print("The file does not exist")
                packet_list = [Message(PacketType.DATA, 0,"!!! NO PROVIDED DATA !!!")]

            self.__sender.set_content(packet_list)
            self.__sender.start()

        elif operation == PacketType.MOVE: # 1.[ ] 2. [source_file_name] 3.[destination_path]
            msg2 = self.__message.pop(0)
            msg3 = self.__message.pop(0)
            source = msg2.data
            destination = msg3.data
            print(source)
            if os.path.exists(source) and os.path.exists(destination):
                shutil.move(source, destination)
            else:
                print("The file does not exist")

        elif operation == PacketType.UPLOAD:   # 1.[ ]  2. [dst]
            msg2 = self.__message.pop(0)
            #  0-N. [data]
            self.__receiver.start()
            # pachete de tip data mai departe
            file_content = reconstruct_string(self.__receiver.get_ordered_packets())
            destination = msg2.data

            with open(destination, "a") as destination_file:
                destination_file.write(file_content)

        elif operation == PacketType.HIERARCHY:  #1. []
            folder: dict = folder_to_dict("FileExplorerServer")
            json_packets: list[Message] = divide_json(folder)

            self.__sender.set_content(json_packets)
            self.__sender.start()

        elif operation == PacketType.SETTINGS: #1.[] 2.[window_size] 3.[timeout]
            print("*********")
            msg2 = self.__message.pop(0)
            msg3 = self.__message.pop(0)
            window_size = int(msg2.data)
            timeout = float(msg3.data)
            print(window_size)
            print(timeout)
            self.__receiver.set_window_size(window_size)
            self.__sender.set_window_size(window_size)
            self.__sender.set_timeout(timeout)

    def stop(self):
        if self.__receiver:
            self.__receiver.stop()
        if self.__sender:
            self.__sender.stop()

def main():

    server = Server()
    server.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Server stopped")
        server.stop()



if __name__ == "__main__":
    main()