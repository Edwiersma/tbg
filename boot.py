try:
    from cmd import CommandHandler
    from engine import GameState
except:
    pass

handler = CommandHandler()
game = GameState()
handler.engine_interface = game.handler_interface

def intro():
    return game.run_intro()

def send_cmd(cmd: str) -> str:
    return handler.handle_command(cmd)