try:
    import json

    with open('data/data.json') as json_file:
        GAME_DATA = json.load(json_file)
except:
    pass


class GameState:
    def __init__(self):
        self.player_count = 1
        self.players = []
        self.player = Player()
        self.initialized = {k: False for k in GAME_DATA.get("init").keys()}
        self.init_step = 0
        self.override_commands = ["help", "reset", "credits"]

    def run_intro(self):
        return "\n".join(
            [f"{GAME_DATA.get('credits')}\n\n"] + GAME_DATA.get("game_intro")
        )

    def handler_interface(self, cmd: str | None) -> str:
        for init_set, initialized in self.initialized.items():
            if not initialized:
                return self.initialize(init_set, cmd)
        return str(self.__dict__)

    def initialize(self, init_set, cmd=None):
        steps = GAME_DATA.get("init").get(init_set).get("steps")
        step = steps[self.init_step]
        if cmd is None:
            return step.get("q").format_map(self.__dict__)
        a_required = step.get("a", None)

        if a_required:
            cmd = cmd.lower()
            if isinstance(a_required, list):
                a_list = a_required
                if cmd not in a_list:
                    return step.get("q").format_map(self.__dict__)
            elif isinstance(a_required, str):
                pass

        game_var = step.get("game_var", None)
        if game_var:
            if not self.init_var_override(cmd, game_var):
                self._set_nested(game_var, cmd)

        self.init_step += 1
        if self.init_step >= len(steps):
            self.initialized[init_set] = True
            self.init_step = 0
            return self.handler_interface(None)

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
