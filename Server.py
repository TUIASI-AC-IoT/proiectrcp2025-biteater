import json
import os

from DivideFile import divide_file
from Receiver import Receiver
from ReconstructFile import reconstruct_file
from Sender import Sender


# filename= "transmitor.txt"
# filename_out="receiver.txt"
# packet_list = divide_file(filename)
# x = reconstruct_file(packet_list,filename_out)

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

class Server:
    def __init__(self):
        self.__receiver = Receiver()
        self.__sender = Sender()


    def run(self):
        self.__receiver.start()


def main():
    # server = Server()
    # server.run()
    encode = encode_folder("File_Explorer")
    tree = decode_folder(encode)
    print(json.dumps(tree, indent=4))

if __name__ == "__main__":
    main()