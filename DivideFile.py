from Constant import Constant
from Message import Message, PacketType
from pathlib import Path

def divide_file(filename_obj: Path) -> list[str]:
    packet_list: list[str] = []
    with filename_obj.open("rb") as fd:
        c=0
        while True:
            content = fd.read(Constant.PACKET_SIZE)
            if content == b"":
                break

            packet_list.append(content.decode())
            c+=1
    return packet_list


def divide_str_into_messages(string: str, start_index: int = 0) -> list[Message]:
    packet_list: list[Message] = []
    string_pos = 0
    packet_index = start_index
    max_data_size = Constant.PACKET_SIZE - Constant.HEADER_SIZE

    while string_pos < len(string):
        sliced_filename = string[string_pos:string_pos + max_data_size]
        packet = Message(PacketType.DATA, packet_index, sliced_filename)
        packet_list.append(packet)

        string_pos += max_data_size
        packet_index += 1

    return packet_list
