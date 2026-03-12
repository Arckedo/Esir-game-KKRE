from core.engine import GameState


class PausePhase(GameState):
    def __init__(self):
        pass

    def handle_events(self, events, game):
        for event in events:
            pass

    def update(self, game):
        pass

    def draw(self, screen):
        screen.fill((90, 40, 90))
