import threading
import time
from threading import Thread
from socket import socket, AF_INET, SOCK_DGRAM

from Constant import Constant
from Message import PacketType, Message

content = ["a", "b", "c", "d", "e", "f", "g", "h", "z"]
content_to_message = [Message(PacketType.DATA, i + 1, content[i]) for i in range(0, len(content))]



class Client:
    def __init__(self):
        self.tx_socket = socket(AF_INET, SOCK_DGRAM)
        self.rx_socket = socket(AF_INET, SOCK_DGRAM)

        self.__host = "127.0.0.1"
        self.__tx_port = 5000
        self.__rx_port = 6000

        self.tx_socket.bind((self.__host, self.__tx_port))
        self.rx_socket.bind((self.__host, self.__rx_port))

        self.rx_socket.setblocking(False)
        self.tx_socket.setblocking(False)



    def selective_repeat(self):
        global stop_event, content_to_message
        current_packet = 0
        while not stop_event.is_set() :

            try:
                if next_event.is_set():
                    # am trimis o fereastra de pachete
                    for i in range (current_packet, current_packet + Constant.window_size.value):
                        if i >= len(content_to_message):
                            stop_event.set()
                        return_code = self.tx_socket.sendto(content_to_message[i].serialize(), (self.__host, self.__rx_port))
                        if not return_code:
                            print("Server disconnected")
                            return 1
                    current_packet += Constant.window_size.value
                    next_event.clear()
            except (KeyboardInterrupt, IndexError):
                stop_event.set()
            except BlockingIOError:
                time.sleep(Constant.sleep_time.value)
                continue


        return 0


next_event = threading.Event()
stop_event = threading.Event()
data = 0
receive_packet = {}




def read_input():
    global next_event, stop_event, data
    while not stop_event.is_set():
        try:
            if not next_event.is_set():
                data = input()
                next_event.set()
            time.sleep(Constant.sleep_time.value)
        except (KeyboardInterrupt, EOFError, IndexError):
            stop_event.set()



def main():
    cl = Client()

    thread1 = threading.Thread(target=read_input)
    thread2 = threading.Thread(target=cl.selective_repeat)

    thread1.start()
    thread2.start()

    thread2.join()
    thread1.join()



if __name__ == "__main__":
    main()

