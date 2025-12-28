import os


def reconstruct_file(packet_content, filename):
    print("Reconstructing file")
    relative_path = ""
    files = filename.split('/')
    for i in range(0, len(files)-1):
        relative_path += files[i] + '/'
        if not os.path.exists(relative_path):
            os.mkdir(relative_path)

    with open(filename, "wb") as fd:
        fd.write(packet_content.encode('utf-8'))



def reconstruct_string(packet_list) -> str:
    msg = ""
    for packet in packet_list:
        msg += packet.data
    return msg