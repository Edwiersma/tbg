import sys
import re

DEBUG = sys.platform != 'emscripten'

if DEBUG:
    from cmd_interface import CommandHandler

GAMES = {
    "bjack": ["<red>BLACK</red>-<blue>JACK</blue>", "<red>BLACK</red>-<blue>JACK</blue> in the <green>MATRIX</green>."],
    "dcrawl": ["<orange>Dungeon Crawl</orange>", "A dark fantasy adventure Dungeon Crawler."],
    "solsim": ["<yellow>Solar Sim</yellow>", "Epic Space Sim in Sol. <blue>UNE</blue> VS. <red>MCR</red>."]
}

HELP = {
    "cd":"          Displays the name of or changes the current directory.",
    "date":"        Displays or sets the date.",
    "dir":"         Displays a list of files and subdirectories in a directory.",
    "exit":"        Quits the CMD.EXE program (command interpreter).",
    "help":"        Provides Help information for Windows commands."
}


def _strip_tags(text: str) -> str:
    return re.sub(r'</?[a-zA-Z]+>', '', text)


def _game_by_name(name: str):
    if name in GAMES:
        return name.lower()


class BootSequence():
    def __init__(self):
        self.level = ["\\"]

    def handler_interface(self, cmd: str) -> str:
        cmd_list = cmd.strip().lower().split()
        if not cmd_list or not cmd_list[0]:
            return ""

        game = _game_by_name(cmd_list[0])
        if game:
            return f"__LAUNCH__:{game}"

        if cmd_list[0] == "cd":
            return self.fnc_cd(cmd_list)

        if len(cmd_list) >= 2:
            return f"'{cmd_list[0]}' unknown option: -{' '.join(cmd_list[1:])} See '--help'."

        if cmd_list[0] == "dir":
            return self.fnc_dir()

        if cmd_list[0] == "run":
            if len(self.level[0]) >=2 and self.level[1] in GAMES:
                return f"__LAUNCH__:{game}"

        if "help" in cmd_list[0]:
            return self.fnc_help()

        return f"'{' '.join(cmd_list)}' is not recognized as an internal or external command. See '--help'."

    def fnc_cd(self, cmd_list: list) -> str:
        path = " ".join(cmd_list[1:])
        print(f"### Path: {path}, {path in GAMES}")
        if not path:
            return "\\".join(self.level)
        if path == "..":
            if len(self.level) >= 2:
                self.level.pop()
                return "\\".join(self.level)
        elif path in GAMES:
            self.level.append(path)
            return "\\".join(self.level)
        return "PERMISSION DENIED"

    def fnc_help(self) -> str:
        lines = ["For more information on a specific command, type 'command-name -help'"]
        if self.level[-1] in GAMES:
            lines += [f"{self.level[-1].upper():<12}{GAMES[self.level[-1]][1]}"]
            lines += [f"{'RUN':<12}Launch Program."]
        else:
            lines += [f"{k.upper()}{v}" for k, v in HELP.items()]
        return "\n".join(lines)


    def fnc_dir(self) -> str:
        name_col = max(len(name) for name in GAMES) + 6
        nice_col = max(len(_strip_tags(g[0])) for g in GAMES.values()) + 8
        lines = ["Available games:"]
        for name, (nice_name, desc) in GAMES.items():
            name_padding = " " * (name_col - len(name))
            nice_padding = " " * (nice_col - len(_strip_tags(nice_name)))
            lines.append(f"  <green>{name}</green>{name_padding}{nice_name}{nice_padding}{desc}")
        lines += ["", 'Type a <yellow>game name</yellow> to launch it.']
        return "\n".join(lines)


handler = CommandHandler()
boot_sequence = BootSequence()
handler.engine_interface = boot_sequence.handler_interface

def send_cmd(cmd: str) -> str:
    print(f"### Input Sent: {cmd}")
    return handler.handle_command(cmd)

if DEBUG:
    for test in ["cd root", "help", "cd dcrawl", "dcrawl", "foo"]:
        print(f"\n>>> {test}")
        print(send_cmd(test))
