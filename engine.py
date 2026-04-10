# engine.py — DCRAWL game engine

class GameState:
    def __init__(self):
        self.inventory = []
        self.init_step = 0
        self.initialized = False
        self.name = None
        self.time = None

    def initialize(self, cmd):
        if self.init_step == 0:
            self.init_step += 1
            return "\n".join([
                "main.py",
                " ", " ",
                "Welcome, adventurer, to DUNGEON CRAWL.",
                "A realm of darkness rendered in flickering characters and unforgiving logic.",
                "Beneath you lies a labyrinth of ancient stone, where every step deeper into the grid may bring fortune... or doom.",
                "Treasures glint in the shadows, monsters lurk beyond the limits of your sight,",
                "and survival depends not on reflex, but on wit and command. Type carefully the dungeon listens.",
                " ",
                f"Are you sure you want to initialize your adventure? y/n"
            ])

        if self.init_step == 1:
            if cmd == "y":
                self.init_step += 1
                return f"What is your name brave adventurer?"
            else:
                return "__RESET__"

        if self.init_step == 2:
            self.name = cmd
            self.init_step += 1
            return (f"Welcome to land of Munhendia"
                    f"What time is it right now? (Default 12:30pm)")

        if self.init_step == 3:
            return ""

        else:
            return ""



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


state = GameState()

def run_init():
    return state.initialize(cmd=None)

def handle_command(cmd: str) -> str:
    cmd = cmd.strip()
    lower = cmd.lower()
    parts = lower.split()


    if not state.initialized:
        return state.initialize(lower)
