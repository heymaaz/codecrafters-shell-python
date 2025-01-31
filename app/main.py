import sys


def main():
    while True:
        sys.stdout.write("$ ")

        # Wait for user input
        command, parameter = parseInput()
        
        if command=="exit":
            if parameter:
                exit(int(parameter))
            else:
                exit()
        elif command=="echo":
            print(f"{parameter}")
        elif command=="type":
            if parameter:
                cmd = parameter.split(" ")[0]
                if cmd in ['echo', 'type', 'exit']:
                    print(f"{cmd} is a shell builtin")
                else:
                    print(f"{cmd} not found")
        else:
            print(f"{command}: command not found")

def parseInput():
    command = input()
    parameter=""
    if(command.find(" ")>=0):
        parameter = command[1+command.find(" "):]
        command = command[0:command.find(" ")]
    return command,parameter


if __name__ == "__main__":
    main()
