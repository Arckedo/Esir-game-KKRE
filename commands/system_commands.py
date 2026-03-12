from core.engine import Command

class TogglePauseMenuCommand:
    def execute(self, game):
        from states.menu.pause import PausePhase
        game.manager.push(PausePhase())

class BackToPreviousStateCommand:
    def execute(self, game):
        game.manager.pop()

class QuitGameCommand:
    def execute(self, game):
        game.running = False