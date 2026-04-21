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
            list(GAME_DATA["character_classes"].keys()),
            "/".join(v["class_weapon"] for v in GAME_DATA["character_classes"].values())
        ]

    def init_var_override(self, cmd, game_var):
        if game_var == "player_class":
            # Match the typed weapon back to a class key
            matched = [
                k for k, v in GAME_DATA["character_classes"].items()
                if cmd.lower() in v["class_weapon"].lower()
            ]
            if not matched:
                print(f"No class matched for input: {cmd}")
                return False
            class_key = matched[0]
            # Store the full class dict so {player_class[desc]} resolves via format_map
            self.player.player_class = GAME_DATA["character_classes"][class_key]
            return True
        elif game_var == "player_name":
            self.player.player_name = f"<purple>{cmd}</purple>"
            return True

        return False


handler = CommandHandler()
game = DCRAWL()
handler.engine_interface = game.handler_interface


def intro():
    first_question = next(iter(GAME_DATA["init"].values()))["steps"][0]["q"]
    return f"{game.run_intro()}\n\n{first_question}"


def send_cmd(cmd: str) -> str:
    return handler.handle_command(cmd)


if DEBUG:
    print(intro())
    print(send_cmd("y"))
    print(send_cmd("Bob"))
    print(send_cmd("sword"))
    print(send_cmd("am"))
    print(send_cmd("8"))
    # print(game.__dict__)