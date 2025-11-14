import os
from asyncio import sleep


def main():

    fd_position = 0
    with open("../test.txt","r") as fd:
        # print(fd.readline(3))

        c=0
        while True:
            print(f"\tPACKET {c}")
            content= fd.read(10)
            if content == "":
                break
                
            #trimitere continut pe thread
            print(content)

            #primire continut de la transmitator

            c+=1

        missed_packet = 2
        print(f"\n\tCaut un packet pierdut...${missed_packet}...")
        fd.seek(missed_packet*10+1)
        print(fd.read(10))



if __name__ == '__main__':
    main()

