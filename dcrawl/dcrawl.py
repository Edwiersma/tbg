import json
import sys

DEBUG = sys.platform != 'emscripten'

if DEBUG:
    from cmd import CommandHandler
    from engine import GameInit
    with open('dcrawl.json') as json_file:
        GAME_DATA = json.load(json_file)

def get_player_classes():
    return [GAME_DATA["object_definition"].get(c) for c in GAME_DATA["character_classes"]]

class DCRAWL_Init(GameInit):
    def __init__(self):
        super().__init__()
        self.character_classes = (
            [c.get("class_weapon").lower() for c in get_player_classes()],
            "/".join([f"<{c.get('color')}>{c.get('class_weapon')}</{c.get('color')}>" for c in get_player_classes()])
        )

    def fnc_set_player_class(self, cmd):
        matched = [
            c for c in get_player_classes()
            if cmd.lower() in c["class_weapon"].lower()
        ]
        class_key = matched[0].get("name").lower()
        self.player.player_class = GAME_DATA["object_definition"][class_key]

handler = CommandHandler()
game_init = DCRAWL_Init()
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
    print(send_cmd("2"))
    print(send_cmd("Bob"))
    print(send_cmd("Bow"))
    print(send_cmd("n"))
    print(send_cmd("James"))
    print(send_cmd("Bow"))
    print(send_cmd("y"))
    print(send_cmd("Ann"))
    print(send_cmd("Magic"))
    print(send_cmd("y"))
