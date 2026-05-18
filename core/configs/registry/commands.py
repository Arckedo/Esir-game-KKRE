from commands.move_commands import *
from commands.system_commands import *

TD_MOVE_COMMANDS = {
    "top_manette": MoveTopCommand(),
    "top": MoveTopCommand(),
    "left": MoveLeftCommand(),
    "right": MoveRightCommand(),
    "down": MoveDownCommand(),
    "roll": RollCommand(),
    "roll_manette": RollCommand(),
    "shoot": ShootCommand(),
    "crouch": CrouchCommand(),
}

SYSTEM_COMMANDS = {
    "pause": TogglePauseMenuCommand(),
    "quit": QuitGameCommand(),
    "back_state": BackToPreviousStateCommand(),
}
