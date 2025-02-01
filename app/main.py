import sys
import os

def main():
    PATH=os.environ.get("PATH")
    while True:
        sys.stdout.write("$ ")

        # Wait for user input

        userInput = input()
        command, parameter = parseInput(userInput)
        match command:
            case "exit":
                if parameter:
                    exit(int(parameter))
                else:
                    exit()
            case "echo":
                print(f"{parameter}")
                continue
            case "type":
                if parameter:
                    cmd = parameter.split(" ")[0]
                    cmd_path = fileFromPath(cmd,PATH)
                    if cmd in ['echo', 'type', 'exit', 'pwd']:
                        print(f"{cmd} is a shell builtin")
                    elif cmd_path is not None:
                        print(f"{cmd} is {cmd_path}")
                    else:
                        print(f"{cmd} not found")
                    continue
            case "pwd":
                if not parameter:
                    print(os.getcwd())
                else:
                    print("pwd: too many arguments")
                continue
            case "cd":
                if not parameter or parameter=="~":
                    os.chdir(os.getenv("HOME"))
                else:
                    if(os.path.isdir(f"{parameter}")):
                        os.chdir(parameter)
                    else:
                        print(f"cd: {parameter}: No such file or directory")
                continue
            case _:
                cmd_file = fileFromPath(command,PATH)
                if cmd_file is not None:
                    os.system(userInput)
                else:
                    print(f"{command}: command not found")

def parseInput(command):
    parameter=""
    if(command.find(" ")>=0):
        parameter = command[1+command.find(" "):]
        parameter = parseQuotes(parameter)
        command = command[0:command.find(" ")]
    return command,parameter

def parseQuotes(parameter):
    inDQ = False
    inSQ = False
    retStr=""
    i=0
    while i < len(parameter):
        if parameter[i:i+1]=="\"":
            inDQ = not inDQ
            i = i+1
            continue
        if not inDQ and parameter[i:i+1]=="\'":
            inSQ = not inSQ
            i = i+1
            continue
        if parameter[i:i+1]=="\\":
            i = i+1
            if i < len(parameter):
                retStr = retStr + parameter[i:i+1]
            i = i+1
            continue
        if inDQ or inSQ:
            retStr = retStr + parameter[i:i+1]
        else:
            if parameter[i:i+1] == " " and retStr[len(retStr)-1:] == " ":
                i = i+1
                continue
            retStr = retStr + parameter[i:i+1]
        i = i+1
    return retStr    

def fileFromPath(cmd,PATH):
    cmd_path = None
    paths = PATH.split(":")
    for path in paths:
        if(os.path.isfile(f"{path}/{cmd}")):
            return f"{path}/{cmd}"
    return None

if __name__ == "__main__":
    main()
