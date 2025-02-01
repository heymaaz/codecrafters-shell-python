import sys
import os

def main():
    PATH=os.environ.get("PATH")
    while True:
        sys.stdout.write("$ ")

        # Wait for user input

        userInput = input()
        command, parameter = parseInput(userInput)
        
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
                paths = PATH.split(":")
                cmd_path = fileFromPath(cmd,PATH)
                if cmd in ['echo', 'type', 'exit', 'pwd']:
                    print(f"{cmd} is a shell builtin")
                elif cmd_path is not None:
                    print(f"{cmd} is {cmd_path}")
                else:
                    print(f"{cmd} not found")
        elif command=="pwd":
            if not parameter:
                print(os.getcwd())
            else:
                print("pwd: too many arguments")
        elif command=="cd":
            if not parameter:
                os.chdir()
            else:
                if(os.path.isdir(f"{parameter}")):
                    os.chdir(parameter)
                else:
                    print(f"cd: {parameter}: No such file or directory")
        else:
            cmd_file = fileFromPath(command,PATH)
            if cmd_file is not None:
                os.system(userInput)
            else:
                print(f"{command}: command not found")

def parseInput(command):
    parameter=""
    if(command.find(" ")>=0):
        parameter = command[1+command.find(" "):]
        command = command[0:command.find(" ")]
    return command,parameter

def fileFromPath(cmd,PATH):
    cmd_path = None
    paths = PATH.split(":")
    for path in paths:
        if(os.path.isfile(f"{path}/{cmd}")):
            return f"{path}/{cmd}"
    return None

if __name__ == "__main__":
    main()
