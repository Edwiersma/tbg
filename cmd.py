class CommandHandler:
    def __init__(self):
        pass

    def handle_command(self, cmd: str) -> str:
        cmd = cmd.strip()
        return self.engine_interface(cmd)


    def engine_interface(self, cmd: str) -> str:
        pass