import pygame

from core.engine import GameState
from core.parralax import ParallaxManager
from entities.platformer.button import Button
from entities.platformer.debug import draw_text


class EndGamePhase(GameState):
    """Menu graphique de fin de partie avec les options rejouer menu et quitter."""

    def __init__(self, winner: int):
        self.winner = winner
        self._setup_background()
        self._setup_ui()

    def _get_button_sprite(self, sheet, row, col, width, height):
        rect = pygame.Rect(col * width, row * height, width, height)
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(sheet, (0, 0), rect)
        return image

    def _setup_ui(self):
        sheet = pygame.image.load(
            "assets/images/menu/titre/Metal Buttons Text.png"
        ).convert_alpha()

        button_w = 64
        button_h = 32

        replay_normal = self._get_button_sprite(sheet, 1, 0, button_w, button_h)
        menu_normal = self._get_button_sprite(sheet, 3, 0, button_w, button_h)
        quit_normal = self._get_button_sprite(sheet, 6, 0, button_w, button_h)

        screen = pygame.display.get_surface()
        screen_w, screen_h = screen.get_size()

        self.center_x = screen_w // 2
        start_y = screen_h // 2 - 30
        gap = 75
        scale = 1.5

        self.replay_button = Button(self.center_x, start_y, replay_normal, scale)
        self.menu_button = Button(self.center_x, start_y + gap, menu_normal, scale)
        self.quit_button = Button(self.center_x, start_y + gap * 2, quit_normal, scale)

    def _setup_background(self):
        """Arrière-plan animé en parallaxe identique au launcher."""
        self.background = ParallaxManager()
        layers = [
            ("menu/Ocean_8/1", 0.02, 0, 0.1, False, 0, 1),
            ("menu/Ocean_8/2", 0.1, 0.02, 0.2, True, 0, 1),
            ("menu/Ocean_8/3", 0.4, 0.05, 0.4, True, 0, 1),
            ("menu/Ocean_8/4", 0.6, 0.07, 0.7, True, 0, 1),
            ("menu/Ocean_8/5", 0.6, 0.07, 0.7, True, 0, 1),
            ("menu/Ocean_8/6", 0.6, 0.07, 0.7, True, 0, 1),
        ]

        for path, s, vs, auto, align, offset_y, scale in layers:
            self.background.add_layer(
                path,
                speed=s,
                v_speed=vs,
                auto_speed=auto,
                align_bottom=align,
                offset_y=offset_y,
                scale=scale,
            )

    def handle_events(self, events, game):
        for event in events:
            if event.type == pygame.QUIT:
                game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self._restart_game(game)
                elif event.key == pygame.K_ESCAPE:
                    self._return_to_menu(game)

    def update(self, game):
        self.background.update()

        if self.replay_button.draw(game.screen):
            self._restart_game(game)

        if self.menu_button.draw(game.screen):
            self._return_to_menu(game)

        if self.quit_button.draw(game.screen):
            game.running = False

    def _restart_game(self, game):
        """Relance une session de jeu propre."""
        from states.phase.platformer import PlatformerPhase

        game.manager.pop()
        game.manager.push(PlatformerPhase())

    def _return_to_menu(self, game):
        """Quitte l'écran de fin pour revenir à l'état inférieur (LaunchPhase)."""
        game.manager.pop()

    def draw(self, screen, current_fps=None):
        screen.fill((20, 20, 30))
        self.background.draw(screen, pygame.Vector2(0, 0))

        text_color = (255, 215, 0) if self.winner in (1, 2) else (255, 255, 255)
        msg = (
            f"Joueur {self.winner} gagne !"
            if self.winner in (1, 2)
            else "Fin de partie !"
        )

        draw_text(screen, msg, (self.center_x - 150, 140), size=54, color=text_color)
        self.replay_button.draw(screen)
        self.menu_button.draw(screen)
        self.quit_button.draw(screen)
