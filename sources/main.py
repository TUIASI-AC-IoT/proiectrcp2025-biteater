
class ServerDeprecated:
    sender_recv = ("127.0.0.1", 8000)
    sender_send = ("127.0.0.1", 7000)
    receiver_recv = ("127.0.0.1", 6000)
    receiver_send = ("127.0.0.1", 5000)

    def __init__(self):
        self.__receiver: Receiver = Receiver(ServerDeprecated.receiver_recv, ServerDeprecated.receiver_send)
        self.__sender = Sender(ServerDeprecated.sender_recv, ServerDeprecated.sender_send)
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
                self.__sender = Sender(ServerDeprecated.sender_recv, ServerDeprecated.sender_send)
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
            file_path = reconstruct_string(self.__receiver.get_ordered_packets())
            if os.path.exists(file_path):
                os.remove(file_path)
            else:
                print("The file does not exist")

        elif operation == PacketType.DOWNLOAD: #  1.[ ]  [path1] [path2] ...
            src = reconstruct_string(self.__receiver.get_ordered_packets())
            if os.path.exists(src):
                data_list = divide_file(Path(src))
                packet_list = [Message(PacketType.DATA, i, data_list[i]) for i in range(len(data_list))]

            else:
                print("The file does not exist")
                packet_list = [Message(PacketType.DATA, 0,"!!! NO PROVIDED DATA !!!")]

            self.__sender.set_content(packet_list)
            self.__sender.start()

        elif operation == PacketType.MOVE: # 1.[ ] [source_file_name1] [source_file_name2]....  [destination_path1] [destination_path2] ...
            src = reconstruct_string(self.__receiver.get_ordered_packets())
            self.__receiver.start()
            dst = reconstruct_string(self.__receiver.get_ordered_packets())

            print(src)
            if os.path.exists(src) and os.path.exists(dst):
                shutil.move(src, dst)
            else:
                print("The file does not exist")

        elif operation == PacketType.UPLOAD:   # 1.[ ]  [dst1] [dst2] ...
            # receive file_name
            destination = reconstruct_string(self.__receiver.get_ordered_packets())
            print("destination = ", destination)
            #  0-N. [data]
            self.__receiver.start()
            # pachete de tip data mai departe
            file_content = reconstruct_string(self.__receiver.get_ordered_packets())

            with open(destination, "w") as destination_file:
                destination_file.write(file_content)

        elif operation == PacketType.HIERARCHY:  #1. []
            folder: dict = folder_to_dict("FileExplorerServer")
            json_packets: list[Message] = divide_json(folder)

            self.__sender.set_content(json_packets)
            self.__sender.start()

        elif operation == PacketType.SETTINGS: #1.[] 2.[window_size] 3.[timeout]
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

