import math

import pygame

from core.configs.registry.commands import SYSTEM_COMMANDS, TD_MOVE_COMMANDS
from core.configs.registry.inputmap import (
    PLATFORMER_PHASE_KEYS_CONTROLLER_PLAYER,
    PLATFORMER_PHASE_KEYS_CONTROLLER_PLAYER_2,
)
from core.engine import GameState
from core.input_manager import InputManager
from core.level_loader import LevelLoader
from core.parralax import ParallaxManager
from core.sound_manager import SoundManager
from entities.Camera import CameraGroup
from entities.components.collision import CollisionComponent
from entities.platformer.button import Button
from entities.platformer.debug import draw_text
from entities.platformer.player import PlayerPlateformer
from states.menu.endgame import EndGamePhase
from states.menu.parametres import SettingsPhase
from UI.ui_timer import UITimerBar


class PlatformerPhase(GameState):
    """Gère la logique et le rendu du mode plateforme."""

    def __init__(self, initial_time=60.0, tbag_heal_rate=1.0, world="world.ldtk"):
        """Initialise la phase du platformer."""
        self.initial_time = initial_time
        self.tbag_heal_rate = tbag_heal_rate
        self.world = world

        # --- Groupes et Systèmes ---
        self.allsprites = CameraGroup()
        self.solids = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.input_manager_p1 = InputManager(
            PLATFORMER_PHASE_KEYS_CONTROLLER_PLAYER, joystick_index=0
        )
        self.input_manager_p2 = InputManager(
            PLATFORMER_PHASE_KEYS_CONTROLLER_PLAYER_2, joystick_index=1
        )
        self.active_debug_button = False
        self.debug_mode = False
        self.debug_mode_text = self.debug_mode
        self.level_debug_surface = None
        self.victory_reached = False
        self._player_label_font = None

        self.isplayerhit = False
        self.last_hit_time = 0
        self.playerhit_duration = 1000

        # Bouton de debug
        self._debug_button_inactive_img = pygame.image.load(
            "assets/images/debug_non_active.png"
        ).convert_alpha()
        self._debug_button_active_img = pygame.image.load(
            "assets/images/debug_active.png"
        ).convert_alpha()

        initial_btn_img = (
            self._debug_button_active_img
            if self.debug_mode
            else self._debug_button_inactive_img
        )
        self.debug_button = Button(100, 200, initial_btn_img, 0.2)

        # --- Initialisation ---
        self._setup_entities()
        self._setup_world()
        self._setup_background()

    def enter(self):
        """Jouer musique de jeu."""
        SoundManager.play_music("musique_jeu", volume=0.25, loop=True)

    def _setup_entities(self):
        """Initialise les joueurs et l'UI."""
        self.player1 = PlayerPlateformer(100, 964, "player_red")
        self.player1.phase = self
        self.player1.add_component("collision", CollisionComponent(self.player1))
        self.player1.max_chrono = self.initial_time
        self.player1.chrono = self.initial_time
        self.allsprites.add(self.player1)

        self.player2 = PlayerPlateformer(2400, 964, "player_blue")
        self.player2.phase = self
        self.player2.add_component("collision", CollisionComponent(self.player2))
        self.player2.max_chrono = self.initial_time
        self.player2.chrono = self.initial_time
        self.allsprites.add(self.player2)

        self.player = self.player1

        screen_w = pygame.display.get_surface().get_width()
        bar_width = 280
        margin = 40

        pos_p1_left = margin
        pos_p2_left = screen_w - bar_width - margin

        self.timer_bar1 = UITimerBar(
            self.player1, left=pos_p1_left, top=90, width=bar_width, height=24
        )
        self.timer_bar2 = UITimerBar(
            self.player2, left=pos_p2_left, top=90, width=bar_width, height=24
        )

    def _setup_world(self):
        """Charge le niveau et positionne les éléments."""
        self.loader = LevelLoader(self)
        try:
            self.loader.load_level(f"assets/levels/{self.world}")
            self._rebuild_level_debug_surface()
            if hasattr(self, "spawn_pos"):
                self.player1.rect.midbottom = self.spawn_pos
                self.player1.movable.pos = pygame.Vector2(self.player1.rect.topleft)

                self.player2.rect.midbottom = (
                    self.spawn_pos[0] + 64,
                    self.spawn_pos[1] - 120,
                )
                self.player2.movable.pos = pygame.Vector2(self.player2.rect.topleft)
            print("Level loaded successfully.")
        except Exception as e:
            print(f"Level Load Error: {e}")

    def _rebuild_level_debug_surface(self):
        """Construit la surcouche debug du masque de collision."""
        self.level_debug_surface = None
        if hasattr(self, "level_mask"):
            self.level_debug_surface = self.level_mask.to_surface(
                setcolor=(255, 0, 0, 80), unsetcolor=(0, 0, 0, 0)
            )

    def _setup_background(self):
        """Configure les couches de parallaxe."""
        self.background = ParallaxManager()
        layers = [
            ("parallax/1", 0.02, 0, 0.1, False),
            ("parallax/2", 0.1, 0.02, 0.2, True),
            ("parallax/3", 0.4, 0.05, 0.4, True),
            ("parallax/4", 0.6, 0.07, 0.7, True),
        ]
        for path, s, vs, auto, align in layers:
            self.background.add_layer(
                path, speed=s, v_speed=vs, auto_speed=auto, align_bottom=align
            )

    def handle_events(self, events, game):
        """Gère les commandes système et les pressions de touches uniques."""
        command_calls_p1 = self.input_manager_p1.get_commands(events)
        command_calls_p2 = self.input_manager_p2.get_commands(events)

        if "top" in command_calls_p1:
            TD_MOVE_COMMANDS["top"].execute(self.player1)
        if "top" in command_calls_p2:
            TD_MOVE_COMMANDS["top"].execute(self.player2)

        if "top_manette" in command_calls_p1:
            TD_MOVE_COMMANDS["top_manette"].execute(self.player1)
        if "top_manette" in command_calls_p2:
            TD_MOVE_COMMANDS["top_manette"].execute(self.player2)

        if "roll" in command_calls_p1:
            TD_MOVE_COMMANDS["roll"].execute(self.player1)
        if "roll" in command_calls_p2:
            TD_MOVE_COMMANDS["roll"].execute(self.player2)

        if "roll_manette" in command_calls_p1:
            TD_MOVE_COMMANDS["roll_manette"].execute(self.player1)
        if "roll_manette" in command_calls_p2:
            TD_MOVE_COMMANDS["roll_manette"].execute(self.player2)

        self.input_manager_p1.call_commands(command_calls_p1, SYSTEM_COMMANDS, game)
        self.input_manager_p2.call_commands(command_calls_p2, SYSTEM_COMMANDS, game)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game.manager.push(SettingsPhase())

    def update(self, game):
        """Met à jour la logique globale du jeu."""
        keys_pressed = pygame.key.get_pressed()

        crouch_key_p1 = PLATFORMER_PHASE_KEYS_CONTROLLER_PLAYER.get("crouch")
        p1_is_holding = False
        if isinstance(crouch_key_p1, (list, tuple)):
            p1_is_holding = any(
                keys_pressed[k] for k in crouch_key_p1 if isinstance(k, int)
            )
        elif isinstance(crouch_key_p1, int):
            p1_is_holding = keys_pressed[crouch_key_p1]

        crouch_key_p2 = PLATFORMER_PHASE_KEYS_CONTROLLER_PLAYER_2.get("crouch")
        p2_is_holding = False
        if isinstance(crouch_key_p2, (list, tuple)):
            p2_is_holding = any(
                keys_pressed[k] for k in crouch_key_p2 if isinstance(k, int)
            )
        elif isinstance(crouch_key_p2, int):
            p2_is_holding = keys_pressed[crouch_key_p2]

        self.player1.update_crouch_state(p1_is_holding)
        self.player2.update_crouch_state(p2_is_holding)

        if self.player1.is_crouching:
            move_calls_p1 = []
        else:
            move_calls_p1 = [
                action
                for action in self.input_manager_p1.get_continuous_commands()
                if action not in {"top", "roll", "crouch"}
            ]

        if self.player2.is_crouching:
            move_calls_p2 = []
        else:
            move_calls_p2 = [
                action
                for action in self.input_manager_p2.get_continuous_commands()
                if action not in {"top", "roll", "crouch"}
            ]

        self.input_manager_p1.call_commands(
            move_calls_p1, TD_MOVE_COMMANDS, self.player1
        )
        self.input_manager_p2.call_commands(
            move_calls_p2, TD_MOVE_COMMANDS, self.player2
        )

        self.allsprites.update(game.dt)
        self._handle_collisions()
        self._update_chrono(game)

        self.allsprites.update_camera_multi([self.player1, self.player2], game.dt)
        self.background.update()

    def _handle_collisions(self):
        """Gère les interactions entre entités."""
        hits1 = pygame.sprite.spritecollide(
            self.player1, self.enemy_projectiles, True, pygame.sprite.collide_mask
        )
        for projectile in hits1:
            self.player1.take_damage(1, source_pos=projectile.rect.center)

        hits2 = pygame.sprite.spritecollide(
            self.player2, self.enemy_projectiles, True, pygame.sprite.collide_mask
        )
        for projectile in hits2:
            self.player2.take_damage(1, source_pos=projectile.rect.center)

        if pygame.time.get_ticks() - self.last_hit_time > self.playerhit_duration:
            self.isplayerhit = False

        hits_between_players = pygame.sprite.collide_mask(self.player1, self.player2)
        if hits_between_players:
            self.player1.take_damage(1, source_pos=self.player2.rect.center)
            self.player2.take_damage(1, source_pos=self.player1.rect.center)

            if not self.isplayerhit:
                if self.player1.skin_variant == "player_red":
                    self.player1.change_skin("player_blue")
                    self.player2.change_skin("player_red")
                else:
                    self.player1.change_skin("player_red")
                    self.player2.change_skin("player_blue")

                SoundManager.play("shoot", volume=2)
                self.last_hit_time = pygame.time.get_ticks()
                self.isplayerhit = True

    def draw(self, screen, current_fps):
        """Rendu de la phase."""
        screen_w, screen_h = screen.get_size()
        screen.fill((20, 20, 90))

        zoom = max(0.1, float(getattr(self.allsprites, "zoom", 1.0)))
        view_w = max(1, int(screen_w / zoom))
        view_h = max(1, int(screen_h / zoom))

        cam_offset = pygame.Vector2(self.allsprites.offset.x, self.allsprites.offset.y)
        world_center = cam_offset + pygame.Vector2(screen_w * 0.5, screen_h * 0.5)

        render_offset = pygame.Vector2(
            math.floor(world_center.x - view_w * 0.5),
            math.floor(world_center.y - view_h * 0.5),
        )

        base_offset = pygame.Vector2(
            math.floor(self.allsprites.offset.x), math.floor(self.allsprites.offset.y)
        )
        self.background.draw(screen, base_offset)

        world_view = pygame.Surface((view_w, view_h), pygame.SRCALPHA)
        world_view.fill((0, 0, 0, 0))

        if hasattr(self, "level_image"):
            world_view.blit(self.level_image, -render_offset)

        self.allsprites.custom_draw(world_view, render_offset, debug=self.debug_mode)
        self._draw_world_debug(world_view, render_offset)

        if view_w == screen_w and view_h == screen_h:
            screen.blit(world_view, (0, 0))
        else:
            scaled_world = pygame.transform.smoothscale(
                world_view, (screen_w, screen_h)
            )
            screen.blit(scaled_world, (0, 0))

        self.affichage_nom_player(
            screen, self.player1, "1", render_offset, view_w, view_h
        )
        self.affichage_nom_player(
            screen, self.player2, "2", render_offset, view_w, view_h
        )

        self._draw_debug_ui(screen, current_fps)
        self.timer_bar1.draw(screen, is_p2=False)
        self.timer_bar2.draw(screen, is_p2=True)

    def _draw_world_debug(self, screen, offset):
        """Affiche les éléments de debug liés au monde (zoomables)."""
        if self.debug_mode and self.level_debug_surface is not None:
            screen.blit(self.level_debug_surface, -offset)

    def _draw_debug_ui(self, screen, current_fps):
        """Affiche les éléments de debug UI (non zoomés)."""
        if self.active_debug_button and self.debug_button.draw(screen):
            self.debug_mode = not self.debug_mode
            self.debug_mode_text = self.debug_mode

            btn_img = (
                self._debug_button_active_img
                if self.debug_mode
                else self._debug_button_inactive_img
            )
            self.debug_button.image = pygame.transform.scale(
                btn_img,
                (int(btn_img.get_width() * 0.2), int(btn_img.get_height() * 0.2)),
            )
            self.debug_button.rect = self.debug_button.image.get_rect(
                topleft=self.debug_button.rect.topleft
            )

        if self.debug_mode_text:
            draw_text(screen, f"Player Pos: {self.player.rect.topleft}", (100, 100))
            draw_text(screen, f"Player2 Pos: {self.player2.rect.topleft}", (100, 120))
            draw_text(screen, f"Player HP: {self.player.hp}", (100, 140))
            draw_text(
                screen, f"Player Invulnerable: {self.player.invulnerable}", (100, 160)
            )
            draw_text(
                screen, f"roll countdown: {self.player.roll_cooldown}", (100, 180)
            )
            draw_text(screen, f"FPS:{current_fps}", (100, 200))

    def _update_chrono(self, game) -> None:
        """Met à jour le chrono selon le rôle + applique le soin tbag."""
        if self.victory_reached:
            return

        dt = game.dt
        chasse_rate = 1.0

        p1_is_thief = self.player1.skin_variant == "player_red"
        p2_is_thief = self.player2.skin_variant == "player_red"

        if not p1_is_thief:
            self.player1.chrono -= chasse_rate * dt
        if not p2_is_thief:
            self.player2.chrono -= chasse_rate * dt

        if p1_is_thief:
            if self.player1.is_crouching:
                self.player1.chrono += self.tbag_heal_rate * dt

        if p2_is_thief:
            if self.player2.is_crouching:
                self.player2.chrono += self.tbag_heal_rate * dt

        # Clamp des valeurs
        self.player1.chrono = max(
            0.0, min(self.player1.max_chrono, self.player1.chrono)
        )
        self.player2.chrono = max(
            0.0, min(self.player2.max_chrono, self.player2.chrono)
        )

        # Conditions de victoire
        winner = None
        if self.player1.chrono <= 0.0:
            self.victory_reached = True
            winner = 2
        elif self.player2.chrono <= 0.0:
            self.victory_reached = True
            winner = 1

        if self.victory_reached:
            game.manager.pop()
            game.manager.push(EndGamePhase(winner))

    def affichage_nom_player(
        self, screen, player, label, render_offset, view_w, view_h
    ):
        """Affiche un label centré au-dessus d'un joueur."""
        if not pygame.font.get_init():
            pygame.font.init()

        if self._player_label_font is None:
            self._player_label_font = pygame.font.SysFont("Roboto", 40)

        scale_x = screen.get_width() / max(1, view_w)
        scale_y = screen.get_height() / max(1, view_h)

        label_surface = self._player_label_font.render(label, True, (255, 255, 255))
        shadow_surface = self._player_label_font.render(label, True, (0, 0, 0))

        world_x = (player.rect.centerx - render_offset.x) * scale_x
        world_y = (player.rect.top - render_offset.y - 26) * scale_y
        label_rect = label_surface.get_rect(center=(int(world_x), int(world_y)))
        shadow_rect = shadow_surface.get_rect(
            center=(label_rect.centerx + 1, label_rect.centery + 1)
        )

        screen.blit(shadow_surface, shadow_rect)
        screen.blit(label_surface, label_rect)

    def exit(self):
        """Arrêter la musique de jeu"""
        SoundManager.stop_music()
