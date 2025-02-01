import sys
import os
from typing import Tuple

class MyCustomError(Exception):
    pass

def main():
    PATH:str = os.environ.get("PATH")
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()

        toFile=None
        toErrorFile=None
        userInput:str = input()
        command, parameter = parseInput(userInput)

        if "1>" in parameter:
            parts = parameter.split("1>", 1)
            parameter = parts[0].strip()
            toFile = parts[1].strip()

        elif "2>" in parameter:
            parts = parameter.split("2>", 1)
            parameter = parts[0].strip()
            toErrorFile = parts[1].strip()
            os.makedirs(os.path.dirname(toErrorFile), exist_ok=True)
            with open(toErrorFile, "a") as file:
                print("", end="", file=file)

        elif ">" in parameter:
            parts = parameter.split(">", 1)
            parameter = parts[0].strip()
            toFile = parts[1].strip()

        output=""
        # print(f"command: {command} parameter: {parameter}, toFile: {toFile}, output: {output}")
        try:
            match command:
                case "exit":
                    if parameter:
                        exit(int(parameter))
                    else:
                        exit()

                case "echo":
                    output=f"{parameter}\n"

                case "type":
                    if parameter:
                        cmd = parameter.split(" ")[0]
                        cmd_path = fileFromPath(cmd,PATH)
                        if cmd in ['echo', 'type', 'exit', 'pwd']:
                            output = f"{cmd} is a shell builtin\n"
                        elif cmd_path is not None:
                            output = f"{cmd} is {cmd_path}\n"
                        else:
                            # output = f"{cmd} not found\n"
                            raise MyCustomError(f"{cmd} not found\n")

                case "pwd":
                    if not parameter:
                        output = f"{os.getcwd()}\n"
                    else:
                        # output = "pwd: too many arguments\n"
                        raise MyCustomError(f"pwd: too many arguments\n")

                case "cd":
                    if not parameter or parameter=="~":
                        os.chdir(os.getenv("HOME"))
                    else:
                        if(os.path.isdir(f"{parameter}")):
                            os.chdir(parameter)
                        else:
                            # output = f"cd: {parameter}: No such file or directory\n"
                            raise MyCustomError(f"cd: {parameter}: No such file or directory\n")

                case _:
                    cmd_file = fileFromPath(command,PATH)
                    if cmd_file is not None:
                        os.system(userInput)
                    else:
                        # output = f"{command}: command not found\n"
                        raise MyCustomError(f"{command}: command not found\n")
                    
        except MyCustomError as e:
            if toErrorFile:
                os.makedirs(os.path.dirname(toErrorFile), exist_ok=True)
                with open(toErrorFile, "a") as file:
                    print(str(e), end="", file=file)
            else:
                print(str(e), end="")
            continue

        if toFile:
            os.makedirs(os.path.dirname(toFile), exist_ok=True)
            with open(toFile, "a") as file:
                print(output, end="", file=file)
        else:
            if output:
                print(output, end="")

def parseInput(userInput:str) -> Tuple[str, str]: 
    parameter = ""
    command = userInput
    userInput = userInput.strip()
    if userInput[0:1]=="\"" or userInput[0:1]=="\'":
        command=userInput[1:userInput.index(userInput[0:1],1)]
        if 2+len(command) < len(userInput):
            parameter=userInput[2+len(command):].strip()
            parameter = parseQuotes(parameter)
        return command,parameter
    else:
        if(userInput.find(" ")>=0):
            parameter = userInput[1+userInput.find(" "):]
            parameter = parseQuotes(parameter)
            command = userInput[0:userInput.find(" ")]
        return command,parameter

def parseQuotes(parameter:str) -> str:
    inDQ = False
    inSQ = False
    retStr=""
    i=0
    while i < len(parameter):
        if not inSQ and parameter[i:i+1]=="\"":
            inDQ = not inDQ
            i = i+1
            continue
        if not inDQ and parameter[i:i+1]=="\'":
            inSQ = not inSQ
            i = i+1
            continue
        if parameter[i:i+1]=="\\" and not inSQ:
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

def fileFromPath(cmd:str, PATH:str) -> (str|None):
    cmd_path = None
    paths = PATH.split(":")
    for path in paths:
        if(os.path.isfile(f"{path}/{cmd}")):
            return f"{path}/{cmd}"
    return None

if __name__ == "__main__":
    main()
