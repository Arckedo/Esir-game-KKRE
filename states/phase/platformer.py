import math

import pygame

from entities.platformer.button import Button
from entities.platformer.debug import draw_text
from core.configs.registry.commands import SYSTEM_COMMANDS, TD_MOVE_COMMANDS
from core.configs.registry.inputmap import PLATFORMER_PHASE_KEYS_PLAYER1, PLATFORMER_PHASE_KEYS_PLAYER2
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
        self.input_manager_p1 = InputManager(PLATFORMER_PHASE_KEYS_PLAYER1, joystick_index=0)
        self.input_manager_p2 = InputManager(PLATFORMER_PHASE_KEYS_PLAYER2, joystick_index=1)
        self.debug_mode = False
        self.debug_mode_text = False
        self.level_debug_surface = None

        # Bouton de debug: inactif au démarrage, actif après clic.
        self._debug_button_inactive_img = pygame.image.load(
            "assets/images/debug_non_active.png"
        ).convert_alpha()
        self._debug_button_active_img = pygame.image.load(
            "assets/images/debug_active.png"
        ).convert_alpha()
        self.debug_button = Button(100, 200, self._debug_button_inactive_img, 0.2)

        # --- Initialisation ---
        self._setup_entities()
        self._setup_world()
        self._setup_background()
        self.cursor = Cursor("crosshair")

    def _setup_entities(self):
        """Initialise le joueur, les ennemis et l'UI."""
        # Joueur1
        self.player1 = PlayerPlateformer(100, 964)
        self.player1.phase = self
        self.player1.add_component("collision", CollisionComponent(self.player1))
        self.allsprites.add(self.player1)

        # Joueur2
        self.player2 = PlayerPlateformer(2400, 964)
        self.player2.phase = self
        self.player2.add_component("collision", CollisionComponent(self.player2))
        self.allsprites.add(self.player2)

        # Compatibilite: le reste du code manipule encore self.player.
        self.player = self.player1

        # Ennemis on les enlèves pour le moment
        #self.enemy = CasterEnemy(1000, 800, self)
        #self.allsprites.add(self.enemy)

        # UI
        self.health_bar1 = UIHealthBar(self.player1, left=10, top=5)
        self.health_bar2 = UIHealthBar(self.player2, left=500, top=5)


    def _setup_world(self):
        """Charge le niveau et positionne les éléments."""
        self.loader = LevelLoader(self)
        try:
            self.loader.load_level("assets/levels/world.ldtk")
            self._rebuild_level_debug_surface()
            if hasattr(self, "spawn_pos"):
                self.player1.rect.midbottom = self.spawn_pos
                self.player1.movable.pos = pygame.Vector2(self.player1.rect.topleft)

                # Spawn proche du joueur1 pour rester dans la zone visible,
                # avec un decalage vertical pour eviter les overlaps de sprite.
                self.player2.rect.midbottom = (self.spawn_pos[0] + 64, self.spawn_pos[1] - 120)
                self.player2.movable.pos = pygame.Vector2(self.player2.rect.topleft)
            print("Level loaded successfully.")
        except Exception as e:
            print(f"Level Load Error: {e}")

    def _rebuild_level_debug_surface(self):
        """Construit une seule fois la surcouche debug du masque de collision."""
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
        """Gère les commandes système (Pause, Quit, etc.)."""
        # Récupère les commandes des deux joueurs
        command_calls_p1 = self.input_manager_p1.get_commands(events)
        command_calls_p2 = self.input_manager_p2.get_commands(events)

        # Sauts (appui unique pour éviter le multi-déclenchement)
        if "top" in command_calls_p1:
            TD_MOVE_COMMANDS["top"].execute(self.player1)
        if "top" in command_calls_p2:
            TD_MOVE_COMMANDS["top"].execute(self.player2)

        # Roulades
        if "roll" in command_calls_p1:
            TD_MOVE_COMMANDS["roll"].execute(self.player1)
        if "roll" in command_calls_p2:
            TD_MOVE_COMMANDS["roll"].execute(self.player2)

        # Commandes système (pause, quit) - pas de différenciation par joueur
        self.input_manager_p1.call_commands(command_calls_p1, SYSTEM_COMMANDS, game)
        self.input_manager_p2.call_commands(command_calls_p2, SYSTEM_COMMANDS, game)

    def update(self, game):
        """Met à jour la logique du jeu."""
        # Réinitialisation frame-based: les commandes continues peuvent réactiver crouch.
        self.player1.is_crouching = False
        self.player2.is_crouching = False

        # 1. Inputs Joueurs (appuis continus)
        move_calls_p1 = [
            action
            for action in self.input_manager_p1.get_continuous_commands()
            if action not in {"top", "roll"}
        ]
        move_calls_p2 = [
            action
            for action in self.input_manager_p2.get_continuous_commands()
            if action not in {"top", "roll"}
        ]
        
        # Applique les commandes de mouvement à chaque joueur
        self.input_manager_p1.call_commands(move_calls_p1, TD_MOVE_COMMANDS, self.player1)
        self.input_manager_p2.call_commands(move_calls_p2, TD_MOVE_COMMANDS, self.player2)

        # 2. Mise à jour des entités et curseur
        self.cursor.update()
        self.allsprites.update(game.dt)
        self._handle_collisions()

        # 3. Caméra multi-cibles: garde player1 et player2 visibles.
        self.allsprites.update_camera_multi(
            [self.player1, self.player2],
            game.dt,
            margin_x=280,
            margin_y=180,
        )
        self.background.update()

    def _handle_collisions(self):
        """Gère les interactions entre entités (projectiles et joueurs)."""
        # Collisions player1
        hits1 = pygame.sprite.spritecollide(
            self.player1, self.enemy_projectiles, True, pygame.sprite.collide_mask
        )
        for projectile in hits1:
            self.player1.take_damage(1, source_pos=projectile.rect.center)

        # Collisions player2
        hits2 = pygame.sprite.spritecollide(
            self.player2, self.enemy_projectiles, True, pygame.sprite.collide_mask
        )
        for projectile in hits2:
            self.player2.take_damage(1, source_pos=projectile.rect.center)

    def draw(self, screen, current_fps):
        """Rendu de la phase."""
        screen_w, screen_h = screen.get_size()
        screen.fill((20, 20, 90))

        # 1) Détermine la zone monde à afficher selon le zoom.
        zoom = max(0.1, float(getattr(self.allsprites, "zoom", 1.0)))
        view_w = max(1, int(screen_w / zoom))
        view_h = max(1, int(screen_h / zoom))

        # Centre caméra actuel en coordonnées monde.
        cam_offset = pygame.Vector2(self.allsprites.offset.x, self.allsprites.offset.y)
        world_center = cam_offset + pygame.Vector2(screen_w * 0.5, screen_h * 0.5)

        # Offset de rendu adapté à la taille de zone visible (view_w/view_h).
        render_offset = pygame.Vector2(
            math.floor(world_center.x - view_w * 0.5),
            math.floor(world_center.y - view_h * 0.5),
        )

        # Background non-zoome: il suit la camera mais conserve son echelle ecran.
        base_offset = pygame.Vector2(
            math.floor(self.allsprites.offset.x), math.floor(self.allsprites.offset.y)
        )
        self.background.draw(screen, base_offset)

        # 2) Rendu du monde sur la zone visible, puis upscale/downscale plein écran.
        world_view = pygame.Surface((view_w, view_h), pygame.SRCALPHA)
        world_view.fill((0, 0, 0, 0))

        # Ordre de rendu : Level -> Entities -> Debug monde

        if hasattr(self, "level_image"):
            world_view.blit(self.level_image, -render_offset)

        self.allsprites.custom_draw(world_view, render_offset, debug=self.debug_mode)
        self._draw_world_debug(world_view, render_offset)

        if view_w == screen_w and view_h == screen_h:
            screen.blit(world_view, (0, 0))
        else:
            scaled_world = pygame.transform.smoothscale(world_view, (screen_w, screen_h))
            screen.blit(scaled_world, (0, 0))

        # 3) UI en overlay (non zoomée)
        self._draw_debug_ui(screen, current_fps)
        self.health_bar1.draw(screen)
        self.health_bar2.draw(screen)
        self.cursor.draw(screen)

    def _draw_world_debug(self, screen, offset):
        """Affiche les éléments de debug liés au monde (zoomables)."""
        if self.debug_mode and self.level_debug_surface is not None:
            screen.blit(self.level_debug_surface, -offset)

    def _draw_debug_ui(self, screen, current_fps):
        """Affiche les éléments de debug UI (non zoomés)."""
        if self.debug_button.draw(screen):
            self.debug_mode = not self.debug_mode
            self.debug_mode_text = self.debug_mode

            if self.debug_mode:
                self.debug_button.image = pygame.transform.scale(
                    self._debug_button_active_img,
                    (
                        int(self._debug_button_active_img.get_width() * 0.2),
                        int(self._debug_button_active_img.get_height() * 0.2),
                    ),
                )
            else:
                self.debug_button.image = pygame.transform.scale(
                    self._debug_button_inactive_img,
                    (
                        int(self._debug_button_inactive_img.get_width() * 0.2),
                        int(self._debug_button_inactive_img.get_height() * 0.2),
                    ),
                )

            self.debug_button.rect = self.debug_button.image.get_rect(
                topleft=self.debug_button.rect.topleft
            )

        if self.debug_mode_text:
            draw_text(screen, f"Player Pos: {self.player.rect.topleft}", (100, 100))
            draw_text(screen, f"Player2 Pos: {self.player2.rect.topleft}", (100, 120))
            draw_text(screen, f"Player HP: {self.player.hp}", (100, 140))
            draw_text(screen, f"Player Invulnerable: {self.player.invulnerable}", (100, 160))
            draw_text(screen, f"roll countdown: {self.player.roll_cooldown}", (100, 180))
            draw_text(screen, f"FPS:{current_fps}", (100, 200))


