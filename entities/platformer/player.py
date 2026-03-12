import pygame

from core.asset_manager import AssetManager
from entities.base_entity import BaseEntity
from entities.components.animator import Animator
from entities.components.movable import MovableComponent
from entities.components.sprite import SpriteComponent
from entities.mask_factory import MaskFactory


class Player(BaseEntity):
    """
    Classe de base pour le joueur gérant les statistiques et les états communs.
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.max_hp = 6
        self.hp = 6

        # États de survie
        self.invulnerable = False
        self.last_hit_time = 0
        self.invincibility_duration = 500  # ms
        self.flash_timer = 0.0

    def take_damage(self, amount: int = 1) -> bool:
        """Applique les dégâts et active le temps de récupération."""
        if not self.invulnerable:
            self.hp -= amount
            self.invulnerable = True
            self.last_hit_time = pygame.time.get_ticks()
            self.flash_timer = 0.15  # Durée du flash blanc/vibration
            return True
        return False

    def update(self, dt: float) -> None:
        """Gère les timers globaux du joueur."""
        if self.invulnerable:
            if (
                pygame.time.get_ticks() - self.last_hit_time
                > self.invincibility_duration
            ):
                self.invulnerable = False

        if self.flash_timer > 0:
            self.flash_timer -= dt

        super().update(dt)


class PlayerPlateformer(Player):
    """
    Spécialisation pour le gameplay de plateforme.
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)

        # --- Physique & Contrôles ---
        self.movable = self.add_component("movable", MovableComponent(self, 700))
        self.facing_right = True
        self.air_time = 0.0
        self.shoot_cooldown = 0.0
        self.cooldown_max = 0.2

        # --- Initialisation Visuelle ---
        self._setup_animations()

        self.base_visual_offset = pygame.Vector2(-75, -36)
        self.shiver_offset = pygame.Vector2(0, 0)

        # Définition de la hitbox physique (Rect + Masque de collision)
        self.rect = pygame.Rect(x, y, 40, 60)
        my_hitbox = MaskFactory.capsule_mask(40, 60)

        self.sprite_comp = self.add_component(
            "sprite",
            SpriteComponent(
                self,
                self.anim_data["idle"][0][0],
                offset=pygame.Vector2(self.base_visual_offset),
                custom_mask=my_hitbox,
            ),
        )

    def _setup_animations(self) -> None:
        """Charge et redimensionne les ressources d'animation."""
        scale = 1.5
        tw, th = int(128 * scale), int(80 * scale)

        def load_scaled(path: str) -> list[pygame.Surface]:
            frames = AssetManager.get_spritesheet(path, 128, 80)
            return [pygame.transform.scale(f, (tw, th)) for f in frames]

        self.anim_data = {
            "run": AssetManager.create_animation_data(
                load_scaled("player/running/running"), 0.08
            ),
            "idle": AssetManager.create_animation_data(
                load_scaled("player/idle/idle"), 0.12
            ),
            "jump": AssetManager.create_animation_data(
                load_scaled("player/jump/up"), 0.1
            ),
            "fall": AssetManager.create_animation_data(
                load_scaled("player/jump/down"), 0.1
            ),
        }
        self.animator = Animator(self, self.anim_data)

    # --- Gestion des Commandes ---
    def moveleft(self) -> None:
        self.movable.input_dir.x = -1

    def moveright(self) -> None:
        self.movable.input_dir.x = 1

    def movetop(self) -> None:
        self.movable.jump(800)

    def movedown(self) -> None:
        self.movable.input_dir.y = 1

    def shoot(self) -> None:
        """Gère le tir en direction de la souris avec offset caméra."""
        if self.shoot_cooldown <= 0:
            from entities.platformer.bullet import Bullet

            mx, my = pygame.mouse.get_pos()
            cam_offset = self.phase.allsprites.offset
            world_mouse = (mx + cam_offset.x, my + cam_offset.y)

            bullet = Bullet(self.rect.centerx, self.rect.centery, world_mouse)
            self.phase.allsprites.add(bullet)
            self.shoot_cooldown = self.cooldown_max

    def take_damage(self, amount: int = 1, source_pos: pygame.Vector2 = None) -> bool:
        """Surcharge pour ajouter un recul (knockback) lors du choc."""
        if super().take_damage(amount):
            if source_pos:
                force = 500
                self.movable.velocity.x = (
                    -force if source_pos.x > self.rect.centerx else force
                )
                self.movable.velocity.y = -350
            return True
        return False

    def update(self, dt: float) -> None:
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

        super().update(dt)

        # 1. Mise à jour de l'état d'animation
        on_ground = getattr(self.movable, "on_ground", True)
        self.air_time = 0.0 if on_ground else self.air_time + dt

        if self.air_time > 0.1:
            self.animator.set_state("jump" if self.movable.velocity.y < 0 else "fall")
        elif abs(self.movable.velocity.x) > 100:
            self.animator.set_state("run")
        else:
            self.animator.set_state("idle")

        self.animator.update(dt)

        # 2. Gestion des effets visuels (Vibration et Clignotement)
        if self.flash_timer > 0:
            self.shiver_offset.x = (pygame.time.get_ticks() % 10) - 5
            self.sprite_comp.visible = True
        else:
            self.shiver_offset.x = 0
            # Effet de clignotement pendant l'invulnérabilité
            self.sprite_comp.visible = (
                not self.invulnerable or (pygame.time.get_ticks() // 80) % 2 == 0
            )

        # 3. Application du flip et des offsets
        self.sprite_comp.offset.x = self.base_visual_offset.x + self.shiver_offset.x

        # Orientation : priorité à la visée à l'arrêt, au mouvement en course
        if abs(self.movable.velocity.x) < 50:
            cam_x = self.phase.allsprites.offset.x
            self.facing_right = (pygame.mouse.get_pos()[0] + cam_x) > self.rect.centerx
        else:
            self.facing_right = self.movable.velocity.x > 0

        self.sprite_comp.flip_x = not self.facing_right
