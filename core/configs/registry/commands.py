from commands.move_commands import *
from commands.system_commands import *

TD_MOVE_COMMANDS = {
    "top": MoveTopCommand(),
    "left": MoveLeftCommand(),
    "right": MoveRightCommand(),
    "down": MoveDownCommand(),
    "shoot": ShootCommand(),
}

SYSTEM_COMMANDS = {
    "pause": TogglePauseMenuCommand(),
    "quit": QuitGameCommand(),
    "back_state": BackToPreviousStateCommand(),
}
