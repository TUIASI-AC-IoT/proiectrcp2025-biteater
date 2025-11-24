from random import random
from time import sleep
from threading import Thread, Timer, Event, RLock
from socket import socket, AF_INET, SOCK_DGRAM
from Constant import Constant
from Message import PacketType, Message


SENDER_ADDR = ("127.0.0.1", 5000)
RECEIVER_ADDR = ("127.0.0.1", 6000)
content_ = ["anna", "belly", "card", "dima", "elisei", "frate", "gica", "hrean", "zoo"]

class Sender(Thread):
    def __init__(self, content=None, packet_type: PacketType = PacketType.INVALID, bind_addr=SENDER_ADDR,
                 receiver_addr=RECEIVER_ADDR):

        super().__init__()
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
        self.__lock = RLock()                              # pentru a schimba continutul variabelor self.timers, self.acked_packets, self.current_packet
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

    def run(self):
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
                raw_data, addr = self.__sock.recvfrom(Constant.PACKET_SIZE.value)
            except OSError: # settimeout() raises this exception
                sleep(0.5)
                continue

            message = Message.deserialize(raw_data)
            if message.packet_type == PacketType.ACK:
                print(f"From __receive_acks, a ack has been received with this content {message}")
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
                    # check for the end
                    if len(self.__acked_packets) >= self.__total_packets:
                        # send end packet to terminate the proccess
                        end_message = Message(PacketType.END, self.__current_packet, "")
                        self.__sock.sendto(end_message.serialize(), self.__receiver_addr)
                        # self.__start_timer(self.__current_packet + 1)

                        self.__running.clear()

    def __send_packet(self, seq: int):

        data = self.__content[seq]
        message = Message(self.__packet_type, seq, data)

        try:
            if random() > Constant.LOSS_PROB.value:              # simulate packet loss
                self.__sock.sendto(message.serialize(), self.__receiver_addr)
            self.__start_timer(seq)
        except OSError as e: # occurs because of sock.settimeout()
            print(f"[Sender] Failed to send data for seq={seq}: {e}")

    def __send_loop(self):
        while self.__running.is_set():
            with self.__lock:
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
            sleep(0.05)
        self.stop()

    def __start_timer(self, seq: int):

        def action_timeout():
            with self.__lock:
                if seq not in self.__acked_packets and self.__running.is_set():
                    print(f"[Sender] TIMEOUT seq={seq}, retransmitting")
                else:
                    return
            self.__send_packet(seq)


        t = Timer(self.__timeout, action_timeout)
        t.daemon = True
        with self.__lock:
            if seq not in self.__acked_packets:
                self.__timers[seq] = t                                  # dictionar seq -> Timer
                t.start()


def test_receive_message():
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(RECEIVER_ADDR)
    while True:
        raw, addr = sock.recvfrom(Constant.PACKET_SIZE.value)
        message = Message.deserialize(raw)

        sock.sendto(Message(PacketType.ACK, message.sequence, message.data + "-ack").serialize(), SENDER_ADDR)
        print(message)

def main():
    sender = Sender(content_,PacketType.DATA)

    # thread1 = Thread(target=test_receive_message)
    # thread1.daemon = True
    # thread1.start()
    # sleep(0.1)
    sender.start()

    sender.join()
if __name__ == "__main__":
    main()