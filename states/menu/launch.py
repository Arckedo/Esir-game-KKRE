import pygame

from core.engine import GameState
from core.parralax import ParallaxManager
from entities.platformer.button import Button
from states.phase.platformer import PlatformerPhase


class LaunchPhase(GameState):
    def __init__(self):
        self._setup_background()
        self._setup_ui()

    def _get_button_sprite(self, sheet, row, col, width, height):
        rect = pygame.Rect(col * width, row * height, width, height)
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(sheet, (0, 0), rect)
        return image


    def _setup_ui(self):
        sheet = pygame.image.load("assets/images/menu/titre/Metal Buttons Text.png").convert_alpha()

        button_w = 64
        button_h = 32

        play_normal = self._get_button_sprite(sheet, 1, 0, button_w, button_h)
        play_hover = self._get_button_sprite(sheet, 1, 1, button_w, button_h)

        settings_normal = self._get_button_sprite(sheet, 3, 0, button_w, button_h)
        settings_hover = self._get_button_sprite(sheet, 3, 1, button_w, button_h)

        quit_normal = self._get_button_sprite(sheet, 6, 0, button_w, button_h)
        quit_hover = self._get_button_sprite(sheet, 6, 1, button_w, button_h)

        screen = pygame.display.get_surface()
        screen_w, screen_h = screen.get_size()

        center_x = screen_w // 2
        start_y = screen_h // 2 - 20
        gap = 75
        scale = 1

        self.play_button = Button(center_x, start_y, play_normal, scale)
        self.settings_button = Button(center_x, start_y + gap, settings_normal, scale)
        self.quit_button = Button(center_x, start_y + gap * 2, quit_normal, scale)

        
    def handle_events(self, events, game):
        for event in events:
            if event.type == pygame.QUIT:
                game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.running = False

    def update(self, game):
        self.background.update()
        if self.play_button.draw(game.screen):
            game.manager.push(PlatformerPhase())
        if self.quit_button.draw(game.screen):
            game.running =False


    def draw(self, screen, current_fps=None):
        screen.fill((40, 40, 40))
        self.background.draw(screen, pygame.Vector2(0, 0))

        the = pygame.image.load("assets/images/menu/Ocean_8/THE.png").convert_alpha()
        scale = 1.5
        the = pygame.transform.smoothscale(
            the,
            (int(the.get_width() * scale), int(the.get_height() * scale))
        )

        x = screen.get_width() // 2 - the.get_width() // 2
        y = 80
        screen.blit(the, (x, y))

        if self.play_button.draw(screen):
            print("PLAY cliqué")

        if self.settings_button.draw(screen):
            print("SETTINGS cliqué")

        if self.quit_button.draw(screen):
            print("QUIT cliqué")

    def _setup_background(self):
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