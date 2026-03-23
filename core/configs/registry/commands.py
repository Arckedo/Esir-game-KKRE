from commands.move_commands import *
from commands.system_commands import *

TD_MOVE_COMMANDS = {
    "top": MoveTopCommand(),
    "left": MoveLeftCommand(),
    "right": MoveRightCommand(),
    "down": MoveDownCommand(),
    "roll": RollCommand(),
    "shoot": ShootCommand(),
    "crouch": CrouchCommand(),
}

SYSTEM_COMMANDS = {
    "pause": TogglePauseMenuCommand(),
    "quit": QuitGameCommand(),
    "back_state": BackToPreviousStateCommand(),
}
