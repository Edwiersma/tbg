try:
    import json
    import random
    with open('data/data.json') as json_file:
        GAME_DATA = json.load(json_file)
except:
    pass


class GameState:
    def __init__(self):
        self.player_count = 1
        self.players = []
        self.player = None
        self.initialized = list([(str(k), None, False) for k in GAME_DATA.get("init").keys()])
        self.init_step = 0
        self.override_commands = ["help", "reset", "credits"]
        self.current_player_num = 0

    def run_intro(self):
        return "\n".join(
            [f"{GAME_DATA.get('credits')}\n\n"] + GAME_DATA.get("game_intro")
        )

    def handler_interface(self, cmd: str | None) -> str:
        for i, (init_name, init_set, initialized) in enumerate(self.initialized):
            if not initialized:
                return self.initialize(i, init_name, init_set, cmd)
        return str(self.__dict__)

    def initialize(self, i, init_name, init_set, cmd=None):
        if not init_set: init_set = init_name
        print(f"initializing {i}, {init_name}, {init_set}, {cmd}, {self.init_step}")
        steps = GAME_DATA.get("init").get(init_set).get("steps")
        step = steps[self.init_step]
        # print(step)
        if cmd is None:
            return step.get("q").format_map(self.__dict__)
        a_required = step.get("a", None)

        cmd_response = ""
        response_list = step.get("r", None)
        if response_list:
            cmd_response = response_list.get(cmd, "")
            if cmd_response:
                cmd_response = f"{random.choice(cmd_response)}\n" if isinstance(cmd_response, list) else f"{cmd_response}\n"
            if response_list.get("_", None):
                cmd_response = f"{response_list.get('_')}\n{cmd_response}"

        if a_required:
            cmd = cmd.lower()
            if isinstance(a_required, list):
                a_list = a_required
                if cmd not in a_list:
                    # print(f"{step.get("q").format_map(self.__dict__)}, {cmd_response}")
                    return cmd_response + step.get("q").format_map(self.__dict__)
            elif isinstance(a_required, str):
                pass

        game_var = step.get("game_var", None)
        if game_var:
            self._set_nested(game_var, cmd)
        game_fnc = step.get("game_fnc", None)
        if game_fnc:
            _fnc_resolved = getattr(self, game_fnc)
            _fnc_resolved(cmd)

        self.init_step += 1
        if self.init_step >= len(steps):
            self.initialized[i] = (init_name, init_set, True)
            self.init_step = 0
            return self.handler_interface(None)

        return cmd_response + steps[self.init_step].get("q").format_map(self.__dict__)

    def _set_nested(self, game_var, value):
        """Supports dot notation e.g. 'player.player_name' -> self.player.player_name"""
        if "." in game_var:
            obj_name, attr = game_var.split(".", 1)
            setattr(getattr(self, obj_name), attr, value)
        else:
            setattr(self, game_var, value)

    def init_var_override(self, cmd, game_var):
        pass

    def fnc_set_player_count(self, cmd):
        self.player_count = int(cmd)
        for i in range(self.player_count):
            self.initialized.insert(i + 2, (f"player_init_{i}", "player_init", False))
        self.initialized.pop(1)

    def fnc_new_player(self, cmd):
        print(f"Created new player: {cmd}")
        self.player = Player(cmd)
        self.players.append(self.player)
        self.current_player_num += 1


class Player:
    def __init__(self, name):
        self.player_name = name
        self.player_class = None
