import sys
import os
import readline
from typing import Tuple

class MyCustomError(Exception):
    pass

builtin = ["echo", "exit", "type", "pwd", "cd"]

def get_commands(PATH):
    """Get all available commands from PATH"""
    commands = set(builtin)
    for path in PATH.split(':'):
        if os.path.isdir(path):
            commands.update(os.listdir(path))
    return commands

def get_path_completions(text):
    """Get completions for file/directory paths"""
    if text.startswith('/'):
        base_path = os.path.dirname(text) or '/'
        partial = os.path.basename(text)
    else:
        base_path = '.'
        partial = text

    try:
        return [f"{os.path.join(base_path, item)}" 
                for item in os.listdir(base_path)
                if item.startswith(partial)]
    except OSError:
        return []
    
def get_common_prefix(matches):
    if not matches:
        return ""
    shortest = min(matches, key=len)
    for i, char in enumerate(shortest):
        if not all(match[i] == char for match in matches):
            return shortest[:i]
    return shortest

def display_matches(text, matches, longest_match_length):
    """Display multiple matches with exactly two spaces between them"""
    buffer = readline.get_line_buffer()
    if matches:
        matches.sort()
        common_prefix = get_common_prefix(matches)
        if common_prefix and common_prefix != text:
            completer.matches = [common_prefix]
        elif len(matches) == 1:
            completer.matches = [matches[0] + " "]
        else:
            # Multiple matches without a longer common prefix
            sys.stdout.write('\a')
            sys.stdout.flush()
            print()
            print("  ".join(matches))
            print("$ " + buffer, end="")
            sys.stdout.flush()
            completer.matches = [text]

def completer(text, state):
    """Enhanced autocomplete function for commands and paths"""
    if state == 0:
        # First time called for this text, build the matches list
        if not text or text[0] not in ['/', '.']:
            # Command completion
            commands = get_commands(os.environ.get("PATH", ""))
            matches = [cmd for cmd in commands if cmd.startswith(text)]
            if len(matches) > 1:
                completer.matches = matches
                # Ring the bell on multiple matches
                sys.stdout.write('\a')
                sys.stdout.flush()
                # Display all matches
                display_matches(text, matches, max(len(m) for m in matches))
            elif len(matches) == 1:
                completer.matches = [matches[0] + " "]
            else:
                completer.matches = []
                # Ring the bell on no matches
                sys.stdout.write('\a')
                sys.stdout.flush()
        else:
            # Path completion
            completer.matches = get_path_completions(text)
            if not completer.matches:
                sys.stdout.write('\a')
                sys.stdout.flush()
    
    return completer.matches[state] if state < len(completer.matches) else None

def setup_readline():
    """Configure readline with proper settings"""
    # Set up readline for different platforms
    if sys.platform == 'darwin':  # macOS
        readline.parse_and_bind("bind ^I rl_complete")
    else:  # Linux and others
        readline.parse_and_bind("tab: complete")
    
    # Set completion settings
    readline.set_completer(completer)
    readline.set_completer_delims(' \t\n;')
    
    # Make completion case-insensitive
    readline.parse_and_bind("set completion-ignore-case on")
    
    # Show all completions if ambiguous
    readline.parse_and_bind("set show-all-if-ambiguous on")


def main():
    PATH = os.environ.get("PATH")
    HOME = os.environ.get("HOME")
    
    # Set up enhanced autocomplete
    setup_readline()


    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()

        toFile=None
        toErrorFile=None
        userInput:str = input()
        command, parameter = parseInput(userInput)

        seps = ['1>>', '2>>', '>>', '1>', '2>', '>']
        for sep in seps:
            if sep in parameter:
                parts = parameter.split(sep, 1)
                parameter = parts[0].strip()

                if '2' in sep:
                    toErrorFile = parts[1].strip()
                    os.makedirs(os.path.dirname(toErrorFile), exist_ok=True)
                    with open(toErrorFile, "a") as file:
                        print("", end="", file=file)
                    continue
                
                toFile = parts[1].strip()
                break


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
                        if cmd in builtin:
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
                        os.chdir(HOME)
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
