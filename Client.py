import threading
import time
from threading import Thread
from socket import socket, AF_INET, SOCK_DGRAM

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

    # def send_message(self):
    #
    #     while True:
    #         try:
    #             # apel non-blocant de send
    #         except BlockingIOError:
    #             time.sleep(0.1)
    #             continue
    #         if not data:
    #             print('Serverul s-a deconectat')
    #             break
    #     return data

    def selective_repeat(self):
        global stop_event
        current_packet = 0
        while not stop_event.is_set():
            try:
                if next_event.is_set():
                    with read_input_available:
                        return_code = self.rx_socket.sendto(content, (self.__host, self.__tx_port))
                        if data and index == int(data):
                            receive_packet[index] = "Receptionat"
                        else:
                            receive_packet[index] = "Pierdut"
                        index += 1
                        next_event.clear()
            except KeyboardInterrupt:
                stop_event.set()

next_event = threading.Event()
stop_event = threading.Event()
read_input_available = threading.Lock()
data = 0
receive_packet = {}




def read_input():
    global next_event, stop_event, data
    while not stop_event.is_set():
        try:
            if not next_event.is_set():
                with read_input_available:
                    data = input()
                    next_event.set()
        except (KeyboardInterrupt, EOFError):
            stop_event.set()



def main():

    thread_de_input = threading.Thread(target=read_input)
    thread_de_increment = threading.Thread(target=selective_repeat)
    thread_de_input.start()
    thread_de_increment.start()

    thread_de_input.join()
    thread_de_input.join()

    print(receive_packet)
    Client()



if __name__ == "__main__":
    main()

