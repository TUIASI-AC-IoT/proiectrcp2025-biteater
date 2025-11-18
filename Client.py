import time
from threading import Thread, Timer, Event, Lock
from socket import socket, AF_INET, SOCK_DGRAM

from jinja2 import PackageLoader

from Constant import Constant
from Message import PacketType, Message

content_ = ["a", "b", "c", "d", "e", "f", "g", "h", "z"]
content_to_message = [Message(PacketType.DATA, i + 1, content_[i]) for i in range(0, len(content_))]

SENDER_ADDR = ("127.0.0.1", 5000)
RECEIVER_ADDR = ("127.0.0.1", 6000)


class Sender:
    def __init__(self, content = None, bind_addr = SENDER_ADDR , receiver_addr = RECEIVER_ADDR):
        if content is None:
            self.content = []
        else:
            self.content = content
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(bind_addr)
        self.receiver_addr = RECEIVER_ADDR

        self.window_size = Constant.WINDOW_SIZE.value
        self.timeout = Constant.PACKET_TIMEOUT.value
        self.current_packet = 0                         # pachetul curent care se transmite
        self.left_window_margin = 0                     # indica indexul din stanga a ferestrei glisante
        self.lock = Lock()                              # pentru a schimba continutul variabelor self.timers, self.acked_packets, self.current_packet
        self.acked_packets = set()                      # o multime de elemente unice
        self.running: Event = Event()
        self.running.set()
        self.timers = {}                                # seq -> Timer

        self.total_packets = len(self.content)
        self.__packet_type = PacketType.INVALID
        # we do not wait for it's termination (daemon = True), it is automatically terminated
        self.__ack_thread = Thread(target=self.__receive_acks, daemon=True)

    def start(self):
        print("Sender is starting...")
        self.sock.settimeout(Constant.SOCK_TIMEOUT.value)
        self.__ack_thread.start()
        self.__send_loop()


    def stop(self):
        self.running.clear()
        with self.lock:
            for t in self.timers.values():
                t.cancel()
        self.sock.close()

    def set_packet_type(self, packet_type: PacketType):
        self.__packet_type = packet_type

    def __receive_acks(self):
        while self.running.is_set():
            try:
                raw_data, addr = self.sock.recvfrom(512)
            except socket.timeout: # because settimeout()
                continue

            message = Message.deserialize(raw_data)
            if message.packet_type.value == "11": # ACK type
                with self.lock:
                    # pentru self.timers ,self.left_window_margin, self.acked_packets (se ruleaza alt thread care porneste timere, si verifica existenta unui ack)
                    # mai exact __send_packet() si __start_timer()
                    if (message.sequence not in self.acked_packets and
                        0 <= message.sequence < self.total_packets):
                        self.acked_packets.add(message.sequence)
                        # cancel timers
                        try:
                            self.timers[message.sequence].cancel()
                            del self.timers[message.sequence]
                        except KeyError:
                            print(f"Failed to delete or cancel the {message.sequence} timer")

                        # we can receive the acks in whichever order so:
                        while self.left_window_margin in self.acked_packets:
                            self.left_window_margin += 1
            with self.lock:
                # self.acked_packets
                if len(self.acked_packets) >= self.total_packets:
                    self.running.clear()

    def __send_packet(self, packet_type: PacketType, seq: int):
        data = self.content[seq]
        message = Message(packet_type, seq, data)
        try:
            self.sock.sendto(message.serialize(), self.receiver_addr)
            self.__start_timer(seq)
        except OSError as e: # occurs because of sock.settimeout()
            print(f"[Sender] Failed to send data for seq={seq}: {e}")

    def __send_loop(self):
        while self.running.is_set():
            with self.lock:
                # self.left_window_margin
                right_window_margin = self.left_window_margin + self.window_size
            while (self.current_packet < self.total_packets and
                   self.current_packet < right_window_margin):
                self.__send_packet(self.__packet_type, self.current_packet)
                self.current_packet += 1
            # check for end
            with self.lock:
                if self.left_window_margin >= self.total_packets:
                    print("[Sender] Sending done.")
                    self.running.clear()
                    break #
            time.sleep(0.05)
        self.stop()

    def __start_timer(self, seq: int):
        def action_timeout():
            # lock in
            if seq not in self.acked_packets:
                print(f"[Sender] TIMEOUT seq={seq}, retransmitting")
                self.__send_packet(seq)

                # restart timer
                self.__start_timer(seq)
            # lock out
        t = Timer(self.timeout, action_timeout)
        t.daemon = True
        t.start()
        self.timers[seq] = t # dictionar seq -> Timer

def main():
    pass



if __name__ == "__main__":
    main()

