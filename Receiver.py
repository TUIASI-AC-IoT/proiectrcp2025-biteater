import select
from threading import Event
import socket
# from socket import AF_INET, SOCK_DGRAM
from Constant import Constant
from Message import PacketType, Message

SENDER_ADDR = ("127.0.0.1", 5000)
RECEIVER_ADDR = ("127.0.0.1", 6000)

class Receiver:
    def __init__(self, bind_addr=RECEIVER_ADDR, sender_addr=SENDER_ADDR,packet_log = None):

        self.__sock: socket.socket | None = None

        self.__bind_addr = bind_addr
        self.__sender_addr = sender_addr
        self.__running: Event = Event()

        self.__window_size: int = Constant.WINDOW_SIZE
        self.__window_base = -1
        self.__expected_total: int | None = None

        self.__buffer: dict = {}  #sequence -> message
        self.__delivered = []
        self.packet_log = packet_log
        self.log_rx_tx = "------------------ RX ---------------------"

    def set_window_size(self, window_size: int):
        self.__window_size = window_size

    def __reset(self):
        self.__delivered.clear()
        self.__buffer.clear()

        self.__window_base = 0
        self.__expected_total: int | None = None
        self.__running.set()


    def start(self) -> None:
        # see same method in Sender for explanation why initialization was moved from
        # "__init__" to "start"
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Permite refolosirea adresei imediat
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.bind(self.__bind_addr)
        self.print_rx()
        print("Receiver started")
        self.__reset()

        self.__receive_loop()

    def stop(self):
        self.__running.clear()
        if self.__sock:
            self.__sock.close()
        print("Receiver stopped")

    def __send_ack(self,seq):
        ack = Message(PacketType.ACK,seq,"")
        self.__sock.sendto(ack.serialize(), self.__sender_addr)

    def print_packets(self,txt):
        if self.packet_log:
            self.packet_log(str(txt))
    def print_rx(self):
        if self.log_rx_tx:
            self.print_packets(self.log_rx_tx)
    def process_packet(self,message):
        seq = message.sequence
        print(message)
        self.print_packets(message)
        # 1. END packet -> set total packets to receive
        if message.packet_type == PacketType.END:
            self.__expected_total = seq
            self.__send_ack(seq)
            return

        # 2. If it's duplicated or deprecated
        if seq in self.__buffer or seq < self.__window_base:
            self.__send_ack(seq)
            return

        # 3. Verify if seq it's out of window -> too new
        if seq >= self.__window_base + self.__window_size:
            return

        # 4. Valid packet
        self.__buffer[seq] = message
        self.__send_ack(seq)

        # 5. Process packet -> deliver
        while self.__window_base in self.__buffer:
            msg = self.__buffer.pop(self.__window_base)
            self.__delivered.append(msg)
            self.__window_base += 1

    def __receive_loop(self):
        while self.__running.is_set():
            try:
                ready, _, _ = select.select([self.__sock], [], [], Constant.SOCK_TIMEOUT)
                if ready:

                    raw_data, addr = self.__sock.recvfrom(Constant.PACKET_SIZE)
                    message = Message.deserialize(raw_data)

                    self.process_packet(message)

                    # 6. Stop: we received END + all packets
                    if self.__expected_total is not None and self.__window_base >= self.__expected_total:
                        for packet in self.__delivered:
                            print(packet.data)
                        self.stop()
                else:
                    # timeout occurred, no data to read
                    pass

            except OSError as e: # failed to receive anything
                print("Error description from __receive_loop: ", e)
                self.stop() # when I press "s" in main menu, get hierarchy operation stops

            except Exception as e:
                print("General Error|description from __receive_loop: ", e)
                self.stop()



    def get_ordered_packets(self):
        return self.__delivered