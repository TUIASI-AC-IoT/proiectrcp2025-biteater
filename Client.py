from Sender import Sender

class Client:
    def __init__(self):
        self.__sender = Sender()


    def __show_menu(self):
        print("Select your command: ")
        print("0: Upload")
        print("1: Download")
        print("2: Delete")
        print("3: Move")
        print("4: Slinding Window Settings")
        resp = input()

        return resp


    def start(self):
        pass

def main():
    pass


if __name__ == "__main__":
    main()

