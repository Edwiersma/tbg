try:
    import json
    with open('data/data.json') as json_file:
        GAME_DATA = json.load(json_file)
except:
    pass


class GameState:
    def __init__(self):
        self.initialized = False
        self.init_step = 0
        self.player_name = None
        self.player_class = None
        self.override_commands = ["help", "reset", "credits"]

    def handler_interface(self, cmd: str) -> str:
        if not self.initialized:
            return self.initialize(cmd)
        return str(self.__dict__)

    def run_intro(self):
        return "\n".join(
            ["<green>engine.py 0.9.0</green> - <blue>Pythonic Games©</blue> - <yellow>1991</yellow>"] + [" "] + [" "]
            + GAME_DATA.get("game_intro")
            + [GAME_DATA.get("game_init").get("steps")[0].get("q")]
        )

    def initialize(self, cmd):
        a_required = GAME_DATA.get("game_init").get("steps")[self.init_step].get("a", None)
        a_list = GAME_DATA.get("game_init").get("steps")[self.init_step].get("a")
        if a_list:
            cmd = cmd.lower()
            if isinstance(a_list, str):
                a_list = a_list.format_map(self.__dict__)
        if not a_required or cmd in a_list:
            game_var = GAME_DATA.get("game_init").get("steps")[self.init_step].get("game_var", None)
            if game_var:
                if not self.init_var_override(cmd, game_var):
                    self.__setattr__(GAME_DATA.get("game_init").get("steps")[self.init_step].get("game_var"), cmd)

            self.init_step += 1
            if self.init_step == len(GAME_DATA.get("game_init").get("steps")):
                self.initialized = True
                return self.handler_interface(cmd)
        return GAME_DATA.get("game_init").get("steps")[self.init_step].get("q").format_map(self.__dict__)

    def init_var_override(self, cmd, game_var):
        pass
