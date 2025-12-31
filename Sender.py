import select
from random import random
from time import sleep
from threading import Thread, Timer, Event, RLock
from Constant import Constant
from Message import PacketType, Message
import socket

SENDER_ADDR = ("127.0.0.1", 5000)
RECEIVER_ADDR = ("127.0.0.1", 6000)
content_ = ["anna", "belly", "card", "dima", "elisei", "frate", "gica", "hrean", "zoo"]
content__ = [Message(PacketType.DATA, i, content_[i]) if i != 0 else Message(PacketType.DELETE, i, content_[i])  for i in range(0, len(content_)) ]

class Sender:
    def __init__(self, bind_addr=SENDER_ADDR, receiver_addr=RECEIVER_ADDR,packet_log = None) -> None:

        self.__content: list[Message] = []

        self.__sock: socket.socket | None = None

        self.__bind_address : str           = bind_addr
        self.__receiver_addr = receiver_addr
        self.__window_size = Constant.WINDOW_SIZE
        self.__timeout = Constant.PACKET_TIMEOUT
        self.__current_packet = 0                         # pachetul curent care se transmite
        self.__left_window_margin = 0                     # indica indexul din stanga a ferestrei glisante
        self.__lock = RLock()                              # pentru a schimba continutul variabelor self.timers, self.acked_packets, self.current_packet
        self.__acked_packets = set()                      # o multime de elemente unice
        self.__running: Event = Event()
        self.__timers = {}                                # seq -> Timer
        self.packet_log = packet_log
        self.__total_packets = len(self.__content)
        self.log_rx_tx = "------------------ TX ---------------------"

    def set_timeout(self, timeout: float) -> None:
        self.__timeout = timeout

    def set_window_size(self, window_size: int) -> None:
        self.__window_size = window_size

    def set_content(self, content: list[Message]) -> None:
        self.__content = content
        self.__current_packet = 0                         # pachetul curent care se transmite
        self.__left_window_margin = 0                     # indica indexul din stanga a ferestrei glisante
        self.__acked_packets.clear()
        self.__timers.clear()
        self.__total_packets = len(self.__content)

    def start(self) -> None:
        print("Sender is starting...")
        self.print_packets(self.log_rx_tx)

        # initialization moved from __init__
        # because I want to work again with the self.__sock after I closed it in previous iteration
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Permite refolosirea adresei imediat
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.bind(self.__bind_address)

        self.__running.set()

        # we do not wait for it's termination (daemon = True), it is automatically terminated
        __ack_thread = Thread(target=self.__receive_acks, daemon=True) # WHY here and not in __init__() ?
        # because, we want to reuse the same object Sender and when reusing you can't start a thread
        # that was previously terminated
        __ack_thread.start()
        self.__send_loop()



    def stop(self):
        self.__running.clear()
        with self.__lock:
            for t in self.__timers.values():
                t.cancel()
        if self.__sock:
            self.__sock.close()
        self.__content.clear()
        print("Sender stopped")

    def print_packets(self,txt):
        if self.packet_log:
            self.packet_log(txt)
    def __receive_acks(self) -> None:
        while self.__running.is_set():

            ready, _, _ = select.select([self.__sock], [], [], Constant.SOCK_TIMEOUT)

            if ready:
                try:
                    raw_data, addr = self.__sock.recvfrom(Constant.PACKET_SIZE)
                except OSError:
                    # WHEN? Occurs when I call "stop" from the ClientGUI class but recvfrom is still running
                    # but, I can not close the socket if it is still running, here comes the exception
                    return
            else: # timeout occurred from select
                continue

            message = Message.deserialize(raw_data)
            if message.packet_type == PacketType.ACK:
                print(f"From __receive_acks, a ack has been received with this content {message}")
                self.print_packets(f"ACK [{message.sequence}]")
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
                        except KeyError as e:
                            print(f"Failed to delete or cancel the {message.sequence} timer")
                            print("Error description: ", e)

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
        message = self.__content[seq]
        if random() > Constant.LOSS_PROB:              # simulate packet loss
            self.__sock.sendto(message.serialize(), self.__receiver_addr)
        self.__start_timer(seq)


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
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(RECEIVER_ADDR)
    while True:
        raw, addr = sock.recvfrom(Constant.PACKET_SIZE)
        message = Message.deserialize(raw)

        sock.sendto(Message(PacketType.ACK, message.sequence, message.data + "-ack").serialize(), SENDER_ADDR)
        print(message)

def main():
    sender = Sender(content__,PacketType.DATA)
    # thread1 = Thread(target=test_receive_message)
    # thread1.daemon = True
    # thread1.start()
    # sleep(0.1)
    sender.start()

if __name__ == "__main__":
    main()