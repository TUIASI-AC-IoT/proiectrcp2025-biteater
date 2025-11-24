from Constant import Constant


def reconstruct_file(packet_list, filename):
    print("Reconstructing file")
    with open(filename, "wb") as fd:
        c = 0
        for packet in packet_list:
            print(f"\tPACKET {c} -> {packet}")

            fd.seek(Constant.PACKET_SIZE.value * c)
            fd.write(packet)
            c += 1