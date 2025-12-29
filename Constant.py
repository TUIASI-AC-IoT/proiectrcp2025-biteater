import struct
from typing import Final

class Constant:
    # Network Configuration
    WINDOW_SIZE: Final[int] = 4
    PACKET_TIMEOUT: Final[float] = 0.5
    INVALID_SEQUENCE: Final[int] = 0
    SLEEP_TIME: Final[float] = 0.1
    LOSS_PROB: Final[float] = 0.4
    SOCK_TIMEOUT: Final[float] = 0.5

    # Protocol / Struct Definitions
    # '2s' = 2 bytes for PacketType (e.g., "11")
    # '!I' = 4 bytes for Sequence Number (Unsigned Integer, Network Byte Order)
    _HEADER_FMT: Final[str] = '!2sI'
    HEADER_SIZE: Final[int] = struct.calcsize(_HEADER_FMT)  # 6 bytes
    PACKET_SIZE: Final[int] = 32 - HEADER_SIZE

    # Filesystem Paths
    CLIENT_FOLDER_PATH: Final[str] = "FileExplorerClient"
    SERVER_FOLDER_PATH: Final[str] = "FileExplorerServer"

    # UI / Messages
    WINDOW_STR: Final[str] = "window_size(int)="
    TIMEOUT_STR: Final[str] = "timeout(float)="
    NO_DATA: Final[str] = "!!! NO PROVIDED DATA !!!"
