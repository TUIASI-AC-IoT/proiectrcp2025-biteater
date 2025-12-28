import json
import os

from Constant import Constant
from Message import Message, PacketType
from ReconstructFile import reconstruct_string


def folder_to_dict(folder_path: str) -> dict:
    tree = {"name" : os.path.basename(folder_path),"type" : "folder", "children" : []}

    for item in os.listdir(folder_path):
        full_path = os.path.join(folder_path, item)
        if os.path.isdir(full_path):
            tree["children"].append(folder_to_dict(full_path))
        else:
            tree["children"].append({"name" : item, "type" : "file"})
    return tree

def encode_folder(folder_path: str):
    tree = folder_to_dict(folder_path)
    return json.dumps(tree)

def decode_folder(json_string):
    return json.loads(json_string)

def divide_json(json_dict : dict):
    json_str: str = json.dumps(json_dict)
    # Constant.PACKET_SIZE.value
    packet_list: list[Message] = list()
    packet_index: int = 0
    string_pos: int = 0

    while string_pos < len(json_str):
        sliced_json = json_str[string_pos : string_pos + Constant.PACKET_SIZE.value]
        packet = Message(PacketType.DATA, packet_index, sliced_json)
        packet_list.append(packet)
        string_pos += Constant.PACKET_SIZE.value
        packet_index += 1

    print(reconstruct_string(packet_list))
    return packet_list