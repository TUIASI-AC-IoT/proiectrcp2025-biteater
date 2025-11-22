import random
import time
from threading import Thread, Timer, Event, Lock
from socket import socket, AF_INET, SOCK_DGRAM
from Constant import Constant
from Message import PacketType, Message
SENDER_ADDR = ("127.0.0.1", 5000)
RECEIVER_ADDR = ("127.0.0.1", 6000)



class Receiver:
    def __init__(self, bind_addr = RECEIVER_ADDR,sender_addr = SENDER_ADDR):

        self.__sock = socket(AF_INET,SOCK_DGRAM)
        self.__sock.bind(bind_addr)
        self.__sender_addr = sender_addr
        self.__running: Event = Event()
        self.__buffer = []
        self.current_packet = None
        self.total_packets_to_receive = 0
        self.total_packets_received = 0
        #use Thread for -> send ACK
        #main process -> process Message


    def start(self):
        print("Receiver started")
        self.__running.set()
        self.__receive_loop()
        self.total_packets_to_receive = 0

    def stop(self):
        self.__running.clear()
        self.__sock.close()

    def __send_acks(self):
        ack = Message(PacketType.ACK,self.current_packet,"")  #send ACK
        self.__sock.sendto(ack.serialize(), self.__sender_addr)

    def process_packet(self,message):

        if self.total_packets_to_receive !=0 : # we received the END packet
            if self.total_packets_received == self.total_packets_to_receive: #verify if we received all packets
                self.stop()

        else:
            index = message.sequence
            packet_exist_in_buffer = False
            for packet in self.__buffer:
                if packet.sequence == index:
                    packet_exist_in_buffer = True
            if not packet_exist_in_buffer:
                self.__buffer.append(message)
                self.total_packets_received += 1


    def __receive_loop(self):
        while self.__running.is_set():
            try:
                raw_data, addr = self.__sock.recvfrom(512)
            except OSError:
                time.sleep(0.5)
                continue

            message = Message.deserialize(raw_data)

            if message.packet_type == PacketType.END:
                # self.stop() # we don't stop it, we may still have packet to receive
                self.total_packets_to_receive = message.sequence - 1

            self.current_packet = message.sequence
            self.__send_acks()
            self.process_packet(message)