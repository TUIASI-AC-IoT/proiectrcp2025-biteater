import struct
from enum import Enum

class Constant(Enum):
    WINDOW_SIZE = 4
    PACKET_TIMEOUT = 0.5
    INVALID_SEQUENCE = 0
    SLEEP_TIME = 0.1
    LOSS_PROB = 0.4
    SOCK_TIMEOUT = 0.5
    # Define the expected packet structure size and format
    # '2s' = 2 bytes for PacketType (e.g., "11")
    # '!I' = 4 bytes for Sequence Number (Unsigned Integer, Network Byte Order)
    HEADER_SIZE = struct.calcsize('!2sI')  # Should be 6 bytes (2 + 4)
    PACKET_SIZE = 32
    WINDOW_STR = "window_size(int)="
    TIMEOUT_STR = "timeout(float)="
    CLIENT_FOLDER_PATH = "FileExplorerClient"
    NO_DATA = "!!! NO PROVIDED DATA !!!"
