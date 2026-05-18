import pygame

from core.engine import GameState
from core.parralax import ParallaxManager
from entities.platformer.button import Button
from core.sound_manager import SoundManager


class SettingsPhase(GameState):
    def __init__(self):
        self._setup_background()
        self._setup_ui()
        self.sound_on = True
        self.fullscreen = False

    def _get_button_sprite(self, sheet, row, col, width, height):
        rect = pygame.Rect(col * width, row * height, width, height)
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(sheet, (0, 0), rect)
        return image

    def _setup_ui(self):
        sheet = pygame.image.load("assets/images/menu/titre/Metal Buttons Text.png").convert_alpha()

        button_w = 64
        button_h = 32

        back_normal = self._get_button_sprite(sheet, 6, 0, button_w, button_h)

        screen = pygame.display.get_surface()
        screen_w, screen_h = screen.get_size()

        center_x = screen_w // 2
        self.back_button = Button(center_x, screen_h - 100, back_normal, 1)

        self.font_title = pygame.font.Font(None, 80)
        self.font_text = pygame.font.Font(None, 42)

    def handle_events(self, events, game):
        for event in events:
            if event.type == pygame.QUIT:
                game.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.manager.pop()
                if event.key == pygame.K_q:
                    SoundManager.set_music_volume(SoundManager.get_music_volume() - 0.1)
                if event.key == pygame.K_d:
                    SoundManager.set_music_volume(SoundManager.get_music_volume() + 0.1)
                if event.key == pygame.K_a:
                    SoundManager.set_sound_volume(SoundManager.get_sound_volume() - 0.1)
                if event.key == pygame.K_e:
                    SoundManager.set_sound_volume(SoundManager.get_sound_volume() + 0.1)


    def update(self, game):
        self.background.update()

        if self.back_button.draw(game.screen):
            game.manager.pop()

    def draw(self, screen, current_fps=None):
        screen.fill((40, 40, 40))
        self.background.draw(screen, pygame.Vector2(0, 0))

        self.back_button.draw(screen)
        music = int(SoundManager.get_music_volume() * 100)
        effects = int(SoundManager.get_sound_volume() * 100)
        txt1 = self.font_text.render(f"Musique : {music}%",True,(255,255,255))
        txt2 = self.font_text.render(f"Effets : {effects}%",True,(255,255,255))
        screen.blit(txt1, (300,220))
        screen.blit(txt2, (300,300))

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