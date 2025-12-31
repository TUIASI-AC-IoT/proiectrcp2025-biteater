import struct
from enum import Enum
from Constant import Constant


class PacketType(Enum):
    UPLOAD = "00"
    DOWNLOAD = "01"
    DELETE ="02"
    MOVE = "03"
    SETTINGS = "04"
    HIERARCHY = "05"
    ACK = "10"
    DATA = "20"
    END = "30"
    INVALID = "55"


class Message:
    def __init__(self,
                 packet_type: PacketType = PacketType.INVALID,
                 sequence: int = Constant.INVALID_SEQUENCE,
                 data:str = ""):

        self.packet_type = packet_type
        self.sequence = sequence
        self.data = data

    def __str__(self):
        return f"[{self.sequence}] PacketType: {self.packet_type.name}, Data: *******PRIVATE DATA******"

    def serialize(self):
        packet_type = self.packet_type.value.encode('ascii') # 2 bytes
        # '!I' = 4 bytes for Sequence Number (Unsigned Integer, Network Byte Order)
        seq = struct.pack('!I', self.sequence)
        data = self.data.encode('utf-8')

        return packet_type + seq + data


    @staticmethod
    def deserialize(data_in):
        try:
            header = data_in[:Constant.HEADER_SIZE]
            # '2s' = 2 bytes for PacketType (e.g., "11")
            # '!I' = 4 bytes for Sequence Number (Unsigned Integer, Network Byte Order)
            packet_type_encoded, sequence = struct.unpack('!2sI', header)
            packet_type = packet_type_encoded.decode('ascii').strip()
            data_encoded = data_in[Constant.HEADER_SIZE:]
            data = data_encoded.decode('utf-8')

            return Message(PacketType(packet_type), sequence, data)

        except struct.error as e:
            print(f"[Deserialize Error] Struct unpacking failed: {e}")
            return Message()
        except (UnicodeDecodeError, ValueError) as e:
            print(f"[Deserialize Error] Data or type decoding failed: {e}")
            return Message()