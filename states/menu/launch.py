from core.engine import GameState


class LaunchPhase(GameState):
    def __init__(self):
        pass

    def handle_events(self, events, game):
        for event in events:
            pass

    def update(self, game):
        pass

    def draw(self, screen):
        screen.fill((40, 40, 40))
