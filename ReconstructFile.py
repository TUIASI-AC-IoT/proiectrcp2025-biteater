import os
from pathlib import Path

def reconstruct_file(packet_content, filename_path: Path):
    print("Reconstructing file")
    relative_path_obj = Path("")
    files = filename_path.parts
    for i in range(0, len(files)-1):
        relative_path_obj /= files[i]
        if not os.path.exists(relative_path_obj):
            os.mkdir(relative_path_obj)

    with open(filename_path, "wb") as fd:
        fd.write(packet_content.encode('utf-8'))



def reconstruct_string(packet_list) -> str:
    msg = ""
    for packet in packet_list:
        msg += packet.data
    return msg