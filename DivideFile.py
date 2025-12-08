from Constant import Constant


def divide_file(filename):
    packet_list = []
    with open(filename, "rb") as fd:
        c=0
        while True:
            content = fd.read(Constant.PACKET_SIZE.value)
            if content == b"":
                break

            packet_list.append(content.decode())
            c+=1
    return packet_list

