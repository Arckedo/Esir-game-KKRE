import pygame

from core.asset_manager import AssetManager
from core.sound_manager import SoundManager
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
        self.max_jumps = 2
        self.jumps_left = self.max_jumps
        self.jump_force = 800
        self.roll_duration = 0.3
        self.roll_cooldown_max = 0.35
        self.roll_speed = 1000
        self.roll_timer = 0.0
        self.roll_cooldown = 0.0
        self.is_rolling = False
        self.roll_direction = 1
        self.roll_buffer_time = 0.12
        self.roll_buffer_timer = 0.0
        self.ground_grace_time = 0.08
        self.ground_grace_timer = 0.0
        self.shoot_cooldown = 0.0
        self.cooldown_max = 0.2
        self.shoot_anim_duration = 0.24
        self.shoot_anim_timer = 0.0
        self.shoot_run_anim_timer = 0.0
        self.is_crouching = False

        # --- Initialisation Visuelle ---
        self._setup_animations()

        self.base_visual_offset = pygame.Vector2(-75, -36)
        self.shiver_offset = pygame.Vector2(0, 0)

        # Définition de la hitbox physique (Rect + Masque de collision)
        # Le point (x, y) est au bas-milieu du joueur, pas au haut-gauche
        self.rect = pygame.Rect(0, 0, 40, 60)
        self.rect.midbottom = (x, y)
        
        # Hitbox standard et réduite pour le crouch
        self.normal_hitbox = MaskFactory.capsule_mask(40, 60)
        self.crouch_hitbox = MaskFactory.capsule_mask(40, 40)  # Hitbox réduite en hauteur
        my_hitbox = self.normal_hitbox

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
            "shoot": AssetManager.create_animation_data(
                load_scaled("player/idle/idle_shoot_gun"), 0.05
            ),
            "shoot_run": AssetManager.create_animation_data(
                load_scaled("player/running/running_shoot_gun"), 0.05
            ),
            "crouch": AssetManager.create_animation_data(
                load_scaled("player/crouch/crouch"), 0.05
            ),
        }

        roll_frames = load_scaled("player/roll/roll")
        if not roll_frames:
            # Fallback : supporte aussi un simple roll.png (1 frame) non découpable en 128x80.
            roll_img = AssetManager.get_image("player/roll/roll")
            if roll_img is not None:
                roll_frames = [pygame.transform.scale(roll_img, (tw, th))]

        if roll_frames:
            self.anim_data["roll"] = AssetManager.create_animation_data(roll_frames, 0.05)
        else:
            # Fallback silencieux si la spritesheet de roulade n'est pas encore prête.
            self.anim_data["roll"] = self.anim_data["run"]

        self.animator = Animator(self, self.anim_data)

    # --- Gestion des Commandes ---
    def moveleft(self) -> None:
        self.movable.input_dir.x = -1

    def moveright(self) -> None:
        self.movable.input_dir.x = 1

    def movetop(self) -> None:
        if self.jumps_left > 0:
            self.movable.velocity.y = -self.jump_force
            self.movable.on_ground = False
            self.jumps_left -= 1
            SoundManager.play("jump", volume=0.35)

    def movedown(self) -> None:
        self.movable.input_dir.y = 1

    def roll(self) -> None:
        """Demande une roulade. La demande est bufferisée quelques ms."""
        if self.roll_timer > 0:
            return

        if abs(self.movable.velocity.x) > 40:
            self.roll_direction = 1 if self.movable.velocity.x > 0 else -1
        else:
            self.roll_direction = 1 if self.facing_right else -1

        self.roll_buffer_timer = self.roll_buffer_time

        if self._can_start_roll():
            self._start_roll()

    def _can_start_roll(self) -> bool:
        """Vérifie si la roulade peut démarrer maintenant."""
        if self.roll_timer > 0 or self.roll_cooldown > 0:
            return False

        return self.movable.on_ground or self.ground_grace_timer > 0

    def _start_roll(self) -> None:
        """Démarre la roulade et consomme la demande bufferisée."""
        self.roll_timer = self.roll_duration
        self.roll_cooldown = self.roll_cooldown_max
        self.roll_buffer_timer = 0.0
        self.is_rolling = True
        SoundManager.play("roll", volume=0.3)

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
            #Tir en courant: on déclenche l'état shoot_run, sinon shoot classique.
            if abs(self.movable.velocity.x) > 100 and self.air_time <= 0.1:
                self.shoot_run_anim_timer = self.shoot_anim_duration
                self.shoot_anim_timer = 0.0
            else:
                self.shoot_anim_timer = self.shoot_anim_duration
                self.shoot_run_anim_timer = 0.0
            

            SoundManager.play("shoot", volume=2)

    def crouch(self) -> None:
        """Active l'état de crouch tant que la touche est maintenue."""
        if self.movable.on_ground:
            self.is_crouching = True

    def uncrouch(self) -> None:
        """Désactive le crouch quand on relâche la touche."""
        self.is_crouching = False

    def take_damage(self, amount: int = 1, source_pos: pygame.Vector2 = None) -> bool:
        """Surcharge pour ajouter un recul (knockback) lors du choc."""
        if super().take_damage(amount):
            SoundManager.play("hit", volume=0.4)
            if source_pos:
                force = 500
                self.movable.velocity.x = (
                    -force if source_pos.x > self.rect.centerx else force
                )
                self.movable.velocity.y = -350
            return True
        return False

    def update(self, dt: float) -> None:
        if self.roll_cooldown > 0:
            self.roll_cooldown -= dt

        if self.roll_buffer_timer > 0:
            self.roll_buffer_timer -= dt

        if self.movable.on_ground:
            self.ground_grace_timer = self.ground_grace_time
        elif self.ground_grace_timer > 0:
            self.ground_grace_timer -= dt

        if self.roll_buffer_timer > 0 and self._can_start_roll():
            self._start_roll()

        if self.roll_timer > 0:
            self.roll_timer -= dt
            self.is_rolling = True
            if self.movable.on_ground or self.ground_grace_timer > 0:
                self.movable.input_dir.x = self.roll_direction
                self.movable.velocity.x = self.roll_direction * self.roll_speed
        else:
            self.is_rolling = False

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

        if self.shoot_anim_timer > 0:
            self.shoot_anim_timer -= dt

        if self.shoot_run_anim_timer > 0:
            self.shoot_run_anim_timer -= dt
        
        super().update(dt)

        # 1. Mise à jour de l'état d'animation
        on_ground = getattr(self.movable, "on_ground", True)
        if on_ground:
            self.jumps_left = self.max_jumps

        self.air_time = 0.0 if on_ground else self.air_time + dt

        if self.shoot_run_anim_timer > 0:
            self.animator.set_state("shoot_run")
        elif self.shoot_anim_timer > 0:
            self.animator.set_state("shoot")
        elif self.is_rolling:
            self.animator.set_state("roll")
        elif self.air_time > 0.1:
            self.animator.set_state("jump" if self.movable.velocity.y < 0 else "fall")
        elif abs(self.movable.velocity.x) > 100:
            self.animator.set_state("run")
        elif self.is_crouching:
            self.animator.set_state("crouch")
            # Applique la hitbox réduite pendant le crouch
            self.sprite_comp.mask = self.crouch_hitbox
        else:
            self.animator.set_state("idle")
            # Restore normal hitbox quand pas de crouch
            self.sprite_comp.mask = self.normal_hitbox

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
