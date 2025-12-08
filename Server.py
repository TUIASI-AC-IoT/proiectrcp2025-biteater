
import shutil


from DivideFile import divide_file
from Message import Message, PacketType
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
        self.__receiver = Receiver(Server.receiver_recv, Server.receiver_send)
        self.__sender = Sender(Server.sender_recv, Server.sender_send)
        self.__message = []

    def start(self):
        self.__receiver.start()
        self.__message = self.__receiver.get_ordered_packets()


        #             #simulare primire mesaj
        # file_path = "File_Explorer/dir1/file2.txt"
        # destination_path = "File_Explorer/dir2"
        # self.__message.append(Message(packet_type=PacketType.MOVE,sequence=0,data=file_path))
        # self.__message.append(Message(packet_type=PacketType.DELETE,sequence=0,data=destination_path))
        #
        # #UPLOAD
        # file_path = "File_Explorer/dir1/file1.txt"
        # content = "HELLO WORLD"
        # destination_path = "File_Explorer/dir2"
        # self.__message.append(Message(packet_type=PacketType.UPLOAD,sequence=0,data=file_path))
        # self.__message.append(Message(packet_type=PacketType.DELETE,sequence=0,data=content))
        self.process_message()



    def process_message(self):
        msg = self.__message.pop(0)
        operation = msg.packet_type

        if operation == PacketType.DELETE: # 1. [ ] 2.[path]
            msg2 = self.__message.pop(0)
            file_path = msg2.data
            if os.path.exists(file_path):
                os.remove(file_path)
            else:
                print("The file does not exist")

        if operation == PacketType.DOWNLOAD: #  1.[ ]  2. [path]
            msg2 = self.__message.pop(0)
            file_path = msg2.data
            if os.path.exists(file_path):
                data_list = divide_file(file_path)
                packet_list = [Message(PacketType.DATA, i, data_list[i]) for i in range(len(data_list))]
                self.__sender.set_content(packet_list)
                self.__sender.start()
            else:
                print("The file does not exist")

        if operation == PacketType.MOVE: # 1.[ ] 2. [source_file_name] 3.[destination_path]
            msg2 = self.__message.pop(0)
            msg3 = self.__message.pop(0)
            source = msg2.data
            destination = msg3.data
            print(source)
            if os.path.exists(source) and os.path.exists(destination):
                shutil.move(source, destination)
            else:
                print("The file does not exist")

        if operation == PacketType.UPLOAD:   # 1.[ ]  2. [file_name]  3.[content]
            msg2 = self.__message.pop(0)
            msg3 = self.__message.pop(0)
            destination = msg2.data
            file_content = reconstruct_string(msg3)

            with open(destination, "a") as destination_file:
                destination_file.write(file_content)



def main():
    server = Server()
    server.start()

    # encode = encode_folder("File_Explorer")
    # tree = decode_folder(encode)
    # print(json.dumps(tree, indent=4))




if __name__ == "__main__":
    main()