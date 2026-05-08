import json
import sys

DEBUG = sys.platform != 'emscripten'

if DEBUG:
    from cmd_interface import CommandHandler
    from engine import GameInit
    try:
        with open('dcrawl.json') as json_file:
            GAME_DATA = json.load(json_file)
    except:
        with open('dcrawl/dcrawl.json') as json_file:
            GAME_DATA = json.load(json_file)


def get_game_data(search_set, key, value):
    return {k: v for k, v in GAME_DATA[search_set].items() if v.get(key) == value}


class GameInitIns(GameInit):
    def __init__(self):
        super().__init__()
        class_dict = get_game_data("object_definition", "object_class", "C_PlayerClass")
        race_dict = get_game_data("object_definition", "object_class", "C_PlayerRace")
        background_dict = get_game_data("object_definition", "object_class", "C_PlayerBackground")
        self.character_classes = (
            [c.get("class_weapon").lower() for c in class_dict.values()],
            " / ".join([f"<{c.get('color')}>{c.get('class_weapon')}</{c.get('color')}>" for c in class_dict.values()])
        )
        self.character_races = (
            [v.get("name").lower() for v in race_dict.values()],
            " / ".join([f"<o>{v}</o>" for v in race_dict.keys()])
        )
        self.character_backgrounds = (
            [v.get("name").lower() for v in background_dict.values()],
            " / ".join([f"<o>{v}</o>" for v in background_dict.keys()])
        )

    def fnc_set_player_class(self, cmd, arg):
        matched = [
            c for c in get_game_data("object_definition", "object_class", "C_PlayerClass").values()
            if cmd.lower() in c["class_weapon"].lower()
        ]
        class_instance = self._create_instance(obj_name=f"{arg}{matched[0].get('name').lower()}", struct=matched[0])
        self.player.player_class = class_instance


handler = CommandHandler()
game_init = GameInitIns()
handler.engine_interface = game_init.handler_interface


def intro():
    first_question = next(iter(GAME_DATA["init"].values()))["steps"][0]["q"]
    return f"{game_init.run_intro()}\n\n{first_question}"


def send_cmd(cmd: str) -> str:
    print(f"### Input Sent: {cmd}")
    return handler.handle_command(cmd)


if DEBUG:
    print(intro())
    print(send_cmd("1"))
    print(send_cmd("Bob"))
    print(send_cmd("half-elf"))
    print(send_cmd("Sword"))
    print(send_cmd("Criminal"))
    print(send_cmd("y"))
    print(send_cmd("5"))
    print(send_cmd("pm"))
