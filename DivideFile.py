from Constant import Constant
from Message import Message, PacketType


def divide_file(filename) -> list[str]:
    packet_list: list[str] = []
    with open(filename, "rb") as fd:
        c=0
        while True:
            content = fd.read(Constant.PACKET_SIZE.value)
            if content == b"":
                break

            packet_list.append(content.decode())
            c+=1
    return packet_list


def divide_filename(filename:str):
    packet_list = []
    string_pos = 0
    packet_index = 0
    max_data_size = Constant.PACKET_SIZE.value - Constant.HEADER_SIZE.value

    while string_pos < len(filename):
        sliced_filename = filename[string_pos:string_pos + max_data_size]
        packet = Message(PacketType.DATA, packet_index, sliced_filename)
        packet_list.append(packet)

        string_pos += max_data_size
        packet_index += 1

    return packet_list
