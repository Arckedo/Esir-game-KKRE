import math

import pygame

from core.configs.registry.commands import SYSTEM_COMMANDS, TD_MOVE_COMMANDS
from core.configs.registry.inputmap import PLATFORMER_PHASE_KEYS
from core.engine import GameState
from core.input_manager import InputManager
from core.level_loader import LevelLoader
from core.parralax import ParallaxManager
from entities.Camera import CameraGroup
from entities.components.collision import CollisionComponent
from entities.cursor import Cursor
from entities.platformer.ennemy import CasterEnemy
from entities.platformer.player import PlayerPlateformer
from UI.ui_element import UIHealthBar


class PlatformerPhase(GameState):
    """Gère la logique et le rendu du mode plateforme."""

    def __init__(self):
        # --- Groupes et Systèmes ---
        self.allsprites = CameraGroup()
        self.solids = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.input_manager = InputManager(PLATFORMER_PHASE_KEYS)
        self.debug_mode = False

        # --- Initialisation ---
        self._setup_entities()
        self._setup_world()
        self._setup_background()
        self.cursor = Cursor("crosshair")

    def _setup_entities(self):
        """Initialise le joueur, les ennemis et l'UI."""
        # Joueur
        self.player = PlayerPlateformer(0, 0)
        self.player.phase = self
        self.player.add_component("collision", CollisionComponent(self.player))
        self.allsprites.add(self.player)

        # Ennemis
        self.enemy = CasterEnemy(1000, 800, self)
        self.allsprites.add(self.enemy)

        # UI
        self.health_bar = UIHealthBar(self.player)

    def _setup_world(self):
        """Charge le niveau et positionne les éléments."""
        self.loader = LevelLoader(self)
        try:
            self.loader.load_level("assets/levels/world.ldtk")
            if hasattr(self, "spawn_pos"):
                self.player.rect.midbottom = self.spawn_pos
                self.player.movable.pos = pygame.Vector2(self.player.rect.topleft)
            print("Level loaded successfully.")
        except Exception as e:
            print(f"Level Load Error: {e}")

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
        """Gère les commandes système (Pause, Quit, etc.)."""
        command_calls = self.input_manager.get_commands(events)

        # Le saut est traité en appui unique (KEYDOWN) pour éviter le multi-déclenchement.
        if "top" in command_calls:
            TD_MOVE_COMMANDS["top"].execute(self.player)
        if "roll" in command_calls:
            TD_MOVE_COMMANDS["roll"].execute(self.player)

        self.input_manager.call_commands(command_calls, SYSTEM_COMMANDS, game)

    def update(self, game):
        """Met à jour la logique du jeu."""
        # 1. Inputs Joueur
        move_calls = [
            action
            for action in self.input_manager.get_continuous_commands()
            if action not in {"top", "roll"}
        ]
        self.input_manager.call_commands(move_calls, TD_MOVE_COMMANDS, self.player)

        # 2. Mise à jour des entités et curseur
        self.cursor.update()
        self.allsprites.update(game.dt)
        self._handle_collisions()

        # 3. Caméra et Environnement
        self.allsprites.update_camera(self.player, game.dt)
        self.background.update()

    def _handle_collisions(self):
        """Gère les interactions entre entités."""
        hits = pygame.sprite.spritecollide(
            self.player, self.enemy_projectiles, True, pygame.sprite.collide_mask
        )
        for projectile in hits:
            self.player.take_damage(1, source_pos=projectile.rect.center)

    def draw(self, screen):
        """Rendu de la phase."""
        screen.fill((20, 20, 90))

        # Synchronisation anti-vibration (Pixel Perfect)
        render_offset = pygame.Vector2(
            math.floor(self.allsprites.offset.x), math.floor(self.allsprites.offset.y)
        )

        # Ordre de rendu : Background -> Level -> Entities -> UI
        self.background.draw(screen, render_offset)

        if hasattr(self, "level_image"):
            screen.blit(self.level_image, -render_offset)

        self.allsprites.custom_draw(screen, render_offset, debug=self.debug_mode)
        self._draw_debug(screen, render_offset)

        self.health_bar.draw(screen)
        self.cursor.draw(screen)

    def _draw_debug(self, screen, offset):
        """Affiche les masques de collision si le mode debug est actif."""
        if self.debug_mode and hasattr(self, "level_mask"):
            level_debug = self.level_mask.to_surface(
                setcolor=(255, 0, 0, 80), unsetcolor=(0, 0, 0, 0)
            )
            screen.blit(level_debug, -offset)
