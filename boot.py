import json
import sys
DEBUG = sys.platform != 'emscripten'

if DEBUG:
    from cmd import CommandHandler
    from engine import GameState
    with open('data/data.json') as json_file:
        GAME_DATA = json.load(json_file)


class DCRAWL(GameState):
    def __init__(self):
        super().__init__()
        self.character_classes = [
            GAME_DATA["character_classes"].keys(), "/".join(GAME_DATA["character_classes"].keys())
        ]

    def init_var_override(self, cmd, game_var):
        if game_var == "player_class":
            self.player_class = GAME_DATA.get("character_classes").get(cmd)
        else:
            return False
        return True


handler = CommandHandler()
game = DCRAWL()
handler.engine_interface = game.handler_interface


def intro():
    return game.run_intro()


def send_cmd(cmd: str) -> str:
    return handler.handle_command(cmd)


if DEBUG:
    print(intro())
    print(send_cmd("y"))
    print(send_cmd("Name"))
    print(send_cmd("sword"))
