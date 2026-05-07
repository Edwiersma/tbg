import json
import sys

DEBUG = sys.platform != 'emscripten'

if DEBUG:
    from cmd_interface import CommandHandler
    from engine import GameInit
    with open('dcrawl.json') as json_file:
        GAME_DATA = json.load(json_file)


def get_game_data(search_set, key, value):
    return {k: v for k, v in GAME_DATA[search_set].items() if v.get(key) == value}


class GameInitIns(GameInit):
    def __init__(self):
        super().__init__()
        class_dict = get_game_data("object_definition", "object_class", "PlayerClass")
        race_dict = get_game_data("object_definition", "object_class", "PlayerRace")
        self.character_classes = (
            [c.get("class_weapon").lower() for c in class_dict.values()],
            "/".join([f"<{c.get('color')}>{c.get('class_weapon')}</{c.get('color')}>" for c in class_dict.values()])
        )
        self.character_races = (
            [k for k in race_dict.keys()],
            "/".join([f"<o>{k}</o>" for k in race_dict.keys()])
        )

    def fnc_set_player_class(self, cmd):
        matched = [
            c for c in get_game_data("object_definition", "object_class", "PlayerClass").values()
            if cmd.lower() in c["class_weapon"].lower()
        ]
        self.player.player_class = self._create_instance(obj_name=matched[0].get("name").lower(), struct=matched[0])


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
    print(send_cmd("y"))
    print(send_cmd("1"))
    print(send_cmd("Bob"))
    print(send_cmd("half-elf"))
    print(send_cmd("Sword"))
    print(send_cmd("Criminal"))
    print(send_cmd("y"))
    print(send_cmd("pm"))
    print(send_cmd("5"))
