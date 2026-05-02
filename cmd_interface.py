def process_command(cmd: str) -> str:
    cmd = cmd.strip()
    return cmd

class CommandHandler:
    def __init__(self):
        pass

    def handle_command(self, cmd: str) -> str:
        return self.engine_interface(process_command(cmd))

    def engine_interface(self, cmd: str) -> str:
        pass