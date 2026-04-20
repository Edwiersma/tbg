try:
    import json
    with open('data/data.json') as json_file:
        GAME_DATA = json.load(json_file)
except:
    pass


class GameState:
    def __init__(self):
        self.player = Player()
        self.initialized = False
        self.init_step = 0
        self.override_commands = ["help", "reset", "credits"]

    def handler_interface(self, cmd: str) -> str:
        if not self.player.initialized:
            return self.initialize("player_init", cmd)
        if not self.initialized:
            return self.initialize("game_init", cmd)
        return str(self.__dict__)

    def run_intro(self):
        return "\n".join(
            [GAME_DATA.get("credits")] + ["\n\n"]
            + GAME_DATA.get("game_intro")
            + [GAME_DATA.get("game_init").get("steps")[0].get("q")]
        )

    def initialize(self, init_set, cmd):
        steps    = GAME_DATA.get(init_set).get("steps")
        step     = steps[self.init_step]
        a_required = step.get("a", None)

        if a_required:
            cmd = cmd.lower()
            # Validate via override if no explicit a list — lets init_var_override decide
            if isinstance(a_required, list):
                a_list = a_required
                if cmd not in a_list:
                    print(f"answer NOT accepted: {a_list}")
                    return step.get("q").format_map(self.__dict__)
            # String-type a fields are handled by init_var_override validation
            elif isinstance(a_required, str):
                pass

        game_var = step.get("game_var", None)
        if game_var:
            if not self.init_var_override(cmd, game_var):
                print("No 'gamevar' Override — using setattr")
                self._set_nested(game_var, cmd)
            else:
                print("'gamevar' Override applied")

        self.init_step += 1
        if self.init_step == len(steps):
            if init_set == "player_init":
                self.player.initialized = True
                self.init_step = 0
                return self.handler_interface(cmd)
            else:
                self.initialized = True
                return self.handler_interface(cmd)

        return steps[self.init_step].get("q").format_map(self.__dict__)

    def _set_nested(self, game_var, value):
        """Supports dot notation e.g. 'player.player_name' -> self.player.player_name"""
        if "." in game_var:
            obj_name, attr = game_var.split(".", 1)
            setattr(getattr(self, obj_name), attr, value)
        else:
            setattr(self, game_var, value)

    def init_var_override(self, cmd, game_var):
        pass


class Player:
    def __init__(self):
        self.initialized = False
        self.player_name = None
        self.player_class = None