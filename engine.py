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
        self.time = None
        self.character_classes = [GAME_DATA["character_classes"].keys(), "/".join(GAME_DATA["character_classes"].keys())]

    def handler_interface(self, cmd: str) -> str:
        if not self.initialized:
            return self.initialize(cmd)

        return str(self.__dict__)

    def run_intro(self):
        return "\n".join(GAME_DATA.get("game_intro")+[GAME_DATA.get("game_init")[0].get("q")])

    def initialize(self, cmd):
        a_required = GAME_DATA.get("game_init")[self.init_step].get("a", None)
        a_list = GAME_DATA.get("game_init")[self.init_step].get("a")
        if a_list:
            cmd = cmd.lower()
            if isinstance(a_list, str):
                a_list = a_list.format_map(self.__dict__)
        if not a_required or cmd in a_list:
            game_var = GAME_DATA.get("game_init")[self.init_step].get("game_var", None)
            if game_var:
                if game_var == "player_class":
                    self.player_class = GAME_DATA.get("character_classes").get(cmd)
                    print(self.player_class)
                else:
                    self.__setattr__(GAME_DATA.get("game_init")[self.init_step].get("game_var"),cmd)
            self.init_step += 1
            if self.init_step == len(GAME_DATA.get("game_init")):
                self.initialized = True
                return self.handler_interface(cmd)
        print(GAME_DATA.get("game_init")[self.init_step].get("q"))
        return GAME_DATA.get("game_init")[self.init_step].get("q").format_map(self.__dict__)

    def help(self):
        return (
            "Available commands:\n"
            "  help        - Show this help message\n"
            "  look        - Look around the current area\n"
            "  inventory   - Show your inventory\n"
            "  credits     - Show credits"
        )

    def credits(self):
        return "Dungeon Crawl v0.1 — A dungeon crawler by Edwiersma"