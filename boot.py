import sys
import re

DEBUG = sys.platform != 'emscripten'

if DEBUG:
    from cmd import CommandHandler

GAMES = {
    "bjack": ["<red>BLACK</red>-<blue>JACK</blue>", "<red>BLACK</red>-<blue>JACK</blue> in the <green>MATRIX</green>"],
    "dcrawl": ["<orange>Dungeon Crawl</orange>", "A dark fantasy adventure Dungeon Crawler"],
    "solsim": ["<yellow>Solar Sim</yellow>", "Epic Space Sim in Sol. <blue>UNE</blue> VS. <red>MCR</red>"]
}

HELP = {
    # "cd":"          Displays the name of or changes the current directory.",
    # "date":"        Displays or sets the date.",
    "dir":"         Displays a list of files and subdirectories in a directory.",
    # "exit":"        Quits the CMD.EXE program (command interpreter).",
    "help":"        Provides Help information for Windows commands."
}


def strip_tags(text: str) -> str:
    print(text)
    return re.sub(r'</?[a-zA-Z]+>', '', text)


def _game_by_name(name: str):
    if name in GAMES:
        return name.lower()


def _dir() -> str:
    name_col = max(len(name) for name in GAMES) + 6
    nice_col = max(len(strip_tags(g[0])) for g in GAMES.values()) + 8
    lines = ["Available games:"]
    for name, (nice_name, desc) in GAMES.items():
        name_padding = " " * (name_col - len(name))
        nice_padding = " " * (nice_col - len(strip_tags(nice_name)))
        lines.append(f"  <green>{name}</green>{name_padding}{nice_name}{nice_padding}{desc}")
    lines += ["", 'Type a <yellow>game name</yellow> to launch it.']
    return "\n".join(lines)


def _help() -> str:
    return "\n".join(
        ["For more information on a specific command, type 'command-name -help'"] +
        [f"{k.upper()}{v}" for k, v in HELP.items()]
    )


def boot_cmd(cmd: str) -> str:
    cmd_list = cmd.strip().lower().split()
    if not cmd_list or not cmd_list[0]:
        return ""

    game = _game_by_name(cmd_list[0])
    if game:
        return f"__LAUNCH__:{game}"

    if len(cmd_list) >= 2:
        return f"'{cmd_list[0]}' unknown option: -{' '.join(cmd_list[1:])} See '--help'."

    if cmd_list[0] == "dir":
        return _dir()

    if "help" in cmd_list[0]:
        return _help()

    return (
        f"'{' '.join(cmd_list)}' is not recognized as an internal or external command. See '--help'."
    )


if DEBUG:
    for test in ["", "help", "dir", "dcrawl", "foo"]:
        print(f"\n>>> {test}")
        print(boot_cmd(test))
