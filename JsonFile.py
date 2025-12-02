import json
import os


def folder_to_dict(folder_path: str) -> dict:
    tree = {"name" : os.path.basename(folder_path),"type" : "folder","children" : []}

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
