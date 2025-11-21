import random
import time
from threading import Thread, Timer, Event, Lock
from socket import socket, AF_INET, SOCK_DGRAM
from Constant import Constant
from Message import PacketType, Message


SENDER_ADDR = ("127.0.0.1", 5000)
RECEIVER_ADDR = ("127.0.0.1", 6000)
content_ = ["a", "b", "c", "d", "e", "f", "g", "h", "z"]
content_to_message = [Message(PacketType.DATA, i + 1, content_[i]) for i in range(0, len(content_))]

class Sender:
    def __init__(self, content = None, packet_type: PacketType = PacketType.INVALID, bind_addr = SENDER_ADDR , receiver_addr = RECEIVER_ADDR):
        if content is None:
            self.__content = []
        else:
            self.__content = content
        self.__sock = socket(AF_INET, SOCK_DGRAM)
        self.__sock.bind(bind_addr)
        self.__receiver_addr = receiver_addr

        self.__window_size = Constant.WINDOW_SIZE.value
        self.__timeout = Constant.PACKET_TIMEOUT.value
        self.__current_packet = 0                         # pachetul curent care se transmite
        self.__left_window_margin = 0                     # indica indexul din stanga a ferestrei glisante
        self.__lock = Lock()                              # pentru a schimba continutul variabelor self.timers, self.acked_packets, self.current_packet
        self.__acked_packets = set()                      # o multime de elemente unice
        self.__running: Event = Event()
        self.__timers = {}                                # seq -> Timer

        self.__total_packets = len(self.__content)
        self.__packet_type = packet_type
        # we do not wait for it's termination (daemon = True), it is automatically terminated
        self.__ack_thread = Thread(target=self.__receive_acks, daemon=True)


    def set_content(self, content, packet_type = PacketType.INVALID):
        self.__content = content
        self.__packet_type = packet_type
        self.__total_packets = len(self.__content)

    def start(self):
        print("Sender is starting...")
        self.__running.set()
        self.__sock.settimeout(Constant.SOCK_TIMEOUT.value)
        self.__ack_thread.start()
        self.__send_loop()


    def stop(self):
        self.__running.clear()
        with self.__lock:
            for t in self.__timers.values():
                t.cancel()
        self.__sock.close()


    def __receive_acks(self):
        while self.__running.is_set():
            try:
                raw_data, addr = self.__sock.recvfrom(512)
            except OSError: # because settimeout()
                time.sleep(0.5)
                continue

            message = Message.deserialize(raw_data)
            if message.packet_type.value == "11": # ACK type
                with self.__lock:
                    # pentru self.timers ,self.left_window_margin, self.acked_packets (se ruleaza alt thread care porneste timere, si verifica existenta unui ack)
                    # mai exact __send_packet() si __start_timer()
                    if (message.sequence not in self.__acked_packets and
                        0 <= message.sequence < self.__total_packets):
                        self.__acked_packets.add(message.sequence)
                        # cancel timers
                        try:
                            self.__timers[message.sequence].cancel()
                            del self.__timers[message.sequence]
                        except KeyError:
                            print(f"Failed to delete or cancel the {message.sequence} timer")

                        # we can receive the acks in whichever order so:
                        while self.__left_window_margin in self.__acked_packets:
                            self.__left_window_margin += 1
            with self.__lock:
                # self.acked_packets
                if len(self.__acked_packets) >= self.__total_packets:
                    self.__running.clear()

    def __send_packet(self, seq: int):
        if random.random() > Constant.LOSS_PROB.value:              # simulate packet loss
            data = self.__content[seq]
            message = Message(self.__packet_type, seq, data)

            try:
                self.__sock.sendto(message.serialize(), self.__receiver_addr)
                self.__start_timer(seq)
            except OSError as e: # occurs because of sock.settimeout()
                print(f"[Sender] Failed to send data for seq={seq}: {e}")

    def __send_loop(self):
        while self.__running.is_set():
            with self.__lock:
                # self.left_window_margin
                right_window_margin = self.__left_window_margin + self.__window_size
            while (self.__current_packet < self.__total_packets and
                   self.__current_packet < right_window_margin):
                self.__send_packet(self.__current_packet)
                self.__current_packet += 1
            # check for end
            with self.__lock:
                if self.__left_window_margin >= self.__total_packets:
                    print("[Sender] Sending done.")
                    self.__running.clear()
                    break #
            time.sleep(0.05)
        self.stop()

    def __start_timer(self, seq: int):

        def action_timeout():
            with self.__lock:
                if seq not in self.__acked_packets:
                    print(f"[Sender] TIMEOUT seq={seq}, retransmitting")
                    self.__send_packet(seq)
                    # restart timer
                    self.__start_timer(seq)

        t = Timer(self.__timeout, action_timeout)
        t.daemon = True
        t.start()
        self.__timers[seq] = t # dictionar seq -> Timer

def test_receive_message():
    while True:
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind(RECEIVER_ADDR)
        raw, addr = sock.recvfrom(512)
        message = Message.deserialize(raw)
        print(message)