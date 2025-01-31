import sys


def main():
    while True:
        sys.stdout.write("$ ")

        # Wait for user input
        command = input()
        parameter=""
        if(command.find(" ")>=0):
            parameter = command[1+command.find(" "):]
            command = command[0:command.find(" ")]
        


        if command=="exit":
            if parameter:
                exit(int(parameter))
            else:
                exit()
        elif command=="echo":
            print(f"{parameter}")
        else:
            print(f"{command}: command not found")

        


if __name__ == "__main__":
    main()
