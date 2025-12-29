from Constant import Constant
from Message import Message, PacketType


# def divide_filename(filename: str):
#     packet_list = []
#     string_pos = 0
#     packet_index = 0
#     max_data_size = Constant.PACKET_SIZE - Constant.HEADER_SIZE
#
#     while string_pos < len(filename):
#         sliced_filename = filename[string_pos:string_pos + max_data_size]
#         packet = Message(PacketType.DATA, packet_index, sliced_filename)
#         packet_list.append(packet)
#
#         string_pos += max_data_size
#         packet_index += 1
#
#     return packet_list

def main():

    packet = divide_filename("dsfdsf/fdsa/f/dsafe/t/y/tjht/h/tg/egwegwe/fwe/f/wef/we/fwe")
    for packet in packet:
        print(packet)



if __name__ == '__main__':
    main()

