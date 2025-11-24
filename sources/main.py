import os
from asyncio import sleep


def main():

    fd_position = 0


    speed = 150
    engine.setProperty('rate', speed)


    with open("../transmitor.txt", "rb") as fd:
        with open("../TemporaryInvalid/received.txt", "wb") as fd_out:
            # print(fd.readline(3))

            c=1
            while True:
                print(f"\tPACKET {c}")
                content= fd.read(10)
                if content == b"":
                    break

                #trimitere continut pe thread
                print(content)

                #primire continut de la transmitator
                #pierdere packet index $3
                if c != 3:
                    fd_out.seek(10*(c-1))
                    fd_out.write(content)

                c+=1

            missed_packet = 3
            print(f"\n\tCaut un packet pierdut...${missed_packet}...")
            fd.seek((missed_packet-1)*10)
            content = fd.read(10)
            fd_out.seek(10*(missed_packet-1))
            fd_out.write(content)



if __name__ == '__main__':
    main()

