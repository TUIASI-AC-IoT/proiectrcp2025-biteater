from enum import Enum
from Constant import Constant

class PacketType(Enum):
    UPLOAD = "00"
    DOWNLOAD = "01"
    DELETE ="02"
    MOVE = "03"
    SETTINGS = "04"
    NAK = "10"
    ACK = "11"
    DATA = "20"
    END = "30"
    INVALID = "55"


class Message:
    def __init__(self,
                 packet_type: PacketType = PacketType.INVALID,
                 sequence: int = Constant.invalid_sequence,
                 data:str = ""):

        self.packet_type = packet_type
        self.sequence = sequence
        self.data = data


    def serialize(self):
        result: str = self.packet_type.value + str(self.sequence) + " " + self.data
        return result.encode()


    @staticmethod
    def deserialize(data_in):
        decoded_data : str = data_in.decode()
        if len(decoded_data) >= 3:
            packet_type = decoded_data[0:2]
            index = 2
            sequence = ""
            while True:
                current_char = decoded_data[index]
                if current_char.isdecimal():
                    sequence += current_char
                elif current_char.isspace():
                    break
                index += 1
            if sequence:
                sequence_int = int(sequence)
            else:
                sequence_int = Constant.invalid_sequence.value
            index += 1
            content = decoded_data[index:]
            return Message(PacketType(packet_type), sequence_int, content)
        return Message()