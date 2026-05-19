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
        self.invincibility_duration = 1000  # ms
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

    def __init__(self, x: int, y: int, skin_variant: str = "player") -> None:
        super().__init__(x, y)
        # Chaque instance peut charger son propre dossier de skin.
        # Permet de brancher chaque instance sur un dossier de skin différent.
        self.skin_variant = skin_variant

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

        # --- Chrono / rôle ---
        self.max_chrono = 60
        self.chrono = self.max_chrono
        self.tbag_nombre = 0

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
        self.crouch_hitbox = MaskFactory.capsule_mask(40, 40)
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

        # Toutes les animations de ce joueur viennent du même sous-dossier.
        # Tous les chemins d'animation partent du skin choisi pour cette instance.
        skin_root = self.skin_variant

        self.anim_data = {
            "run": AssetManager.create_animation_data(
                load_scaled(f"{skin_root}/running/running"), 0.08
            ),
            "idle": AssetManager.create_animation_data(
                load_scaled(f"{skin_root}/idle/idle"), 0.12
            ),
            "jump": AssetManager.create_animation_data(
                load_scaled(f"{skin_root}/jump/up"), 0.1
            ),
            "fall": AssetManager.create_animation_data(
                load_scaled(f"{skin_root}/jump/down"), 0.1
            ),
            "shoot": AssetManager.create_animation_data(
                load_scaled(f"{skin_root}/idle/idle_shoot_gun"), 0.05
            ),
            "shoot_run": AssetManager.create_animation_data(
                load_scaled(f"{skin_root}/running/running_shoot_gun"), 0.05
            ),
            "crouch": AssetManager.create_animation_data(
                load_scaled(f"{skin_root}/crouch/crouch"), 0.05
            ),
        }

        roll_frames = load_scaled(f"{skin_root}/roll/roll")
        if not roll_frames:
            roll_img = AssetManager.get_image(f"{skin_root}/roll/roll")
            if roll_img is not None:
                roll_frames = [pygame.transform.scale(roll_img, (tw, th))]

        if roll_frames:
            self.anim_data["roll"] = AssetManager.create_animation_data(
                roll_frames, 0.05
            )
        else:
            self.anim_data["roll"] = self.anim_data["run"]

        self.animator = Animator(self, self.anim_data)

    # --- Gestion des Commandes ---
    def moveleft(self) -> None:
        # Empêche de courir pendant un tbag toggle actif
        if getattr(self, "_tbag_toggle_active", False):
            return
        self.movable.input_dir.x = -1

    def moveright(self) -> None:
        # Empêche de courir pendant un tbag toggle actif
        if getattr(self, "_tbag_toggle_active", False):
            return
        self.movable.input_dir.x = 1

    def movetop(self) -> None:
        if self.jumps_left > 0:
            self.movable.velocity.y = -self.jump_force
            self.movable.on_ground = False
            self.jumps_left -= 1
            print("MOVETOP")
            SoundManager.play("jump", volume=0.35)

    def movedown(self) -> None:
        self.movable.input_dir.y = 1

    def roll(self) -> None:
        """Demande une roulade. La demande est bufferisée quelques ms."""
        # Ne pas autoriser la roulade pendant un tbag toggle
        if getattr(self, "_tbag_toggle_active", False):
            return
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
            # Tir en courant: on déclenche l'état shoot_run, sinon shoot classique.
            if abs(self.movable.velocity.x) > 100:
                self.shoot_run_anim_timer = self.shoot_anim_duration
                self.shoot_anim_timer = 0.0
            else:
                self.shoot_anim_timer = self.shoot_anim_duration
                self.shoot_run_anim_timer = 0.0

            SoundManager.play("shoot", volume=2)

    def crouch(self) -> None:
        """Active l'état de crouch tant que la touche est maintenue."""
        print(
            f"TBAG/CROUCH déclenché - Skin: {self.skin_variant}, OnGround: {self.movable.on_ground}"
        )

        is_thief = (
            hasattr(self, "phase")
            and hasattr(self.phase, "player1")
            and hasattr(self.phase, "player2")
            and (
                (
                    self == self.phase.player1
                    and self.phase.player1.skin_variant == "player_red"
                )
                or (
                    self == self.phase.player2
                    and self.phase.player2.skin_variant == "player_red"
                )
            )
        )

        print(f"  -> Is Thief: {is_thief}, Skin Variant: {self.skin_variant}")

        if is_thief:
            self.tbag_nombre += 1

            self._tbag_pulse_sequence = [
                (0.08, True),
                (0.05, False),
                (0.08, True),
                (0.05, False),
                (0.08, True),
            ]
            self._tbag_sequence_index = 0
            self._tbag_sequence_timer = self._tbag_pulse_sequence[0][0]
            self.is_crouching = self._tbag_pulse_sequence[0][1]
            print(f"TBAG séquence lancée #{self.tbag_nombre}")

    def uncrouch(self) -> None:
        """Désactive le crouch quand on relâche la touche."""
        self.is_crouching = False

    def take_damage(self, amount: int = 1, source_pos: pygame.Vector2 = None) -> bool:
        """Surcharge pour ajouter un recul (knockback) lors du choc."""
        if super().take_damage(amount):
            SoundManager.play("hit", volume=0.4)
            if source_pos:
                source_x = source_pos.x if hasattr(source_pos, "x") else source_pos[0]
                force = 700
                self.movable.velocity.x = (
                    -force if source_x > self.rect.centerx else force
                )
                self.movable.velocity.y = -350
            return True
        return False

    def update_crouch_state(self, is_holding: bool) -> None:
        """Gère l'état accroupi de manière continue et modifie la hitbox."""
        is_thief = (
            hasattr(self, "phase")
            and hasattr(self.phase, "player1")
            and hasattr(self.phase, "player2")
            and (
                (
                    self == self.phase.player1
                    and self.phase.player1.skin_variant == "player_red"
                )
                or (
                    self == self.phase.player2
                    and self.phase.player2.skin_variant == "player_red"
                )
            )
        )

        if is_holding and not getattr(self, "_tbag_toggle_active", False) and is_thief:
            self._tbag_toggle_active = True
            self._tbag_toggle_interval = 0.06
            self._tbag_toggle_timer = self._tbag_toggle_interval
            self._tbag_toggle_state = True
            self.is_crouching = True
            self.tbag_nombre += 1
            print(f"TBAG toggle start, compteur: {self.tbag_nombre}")

        if not is_holding and getattr(self, "_tbag_toggle_active", False):
            self._tbag_toggle_active = False
            if hasattr(self, "_tbag_toggle_timer"):
                del self._tbag_toggle_timer
            if hasattr(self, "_tbag_toggle_interval"):
                del self._tbag_toggle_interval
            if hasattr(self, "_tbag_toggle_state"):
                del self._tbag_toggle_state
            self.is_crouching = False

        if (
            is_holding
            and not is_thief
            and not getattr(self, "_tbag_toggle_active", False)
        ):
            self.is_crouching = True
        elif not is_holding and not getattr(self, "_tbag_toggle_active", False):
            self.is_crouching = False

        if self.is_crouching:
            if hasattr(self, "sprite_comp"):
                self.sprite_comp.custom_mask = self.crouch_hitbox
            if self.rect.height == 60:
                self.rect.height = 40
        else:
            if hasattr(self, "sprite_comp"):
                self.sprite_comp.custom_mask = self.normal_hitbox
            if self.rect.height == 40:
                self.rect.height = 60

    def update(self, dt: float) -> None:
        self.jeu_gagne()

        if self.roll_cooldown > 0:
            self.roll_cooldown -= dt

        if self.roll_buffer_timer > 0:
            self.roll_buffer_timer -= dt

        if getattr(self, "_tbag_toggle_active", False):
            try:
                self.movable.input_dir.x = 0
                self.movable.velocity.x = 0
            except Exception:
                pass

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

        if getattr(self, "_tbag_toggle_active", False):
            self._tbag_toggle_timer -= dt
            if self._tbag_toggle_timer <= 0:
                self._tbag_toggle_state = not getattr(self, "_tbag_toggle_state", False)
                self.is_crouching = self._tbag_toggle_state
                if self.is_crouching:
                    if hasattr(self, "sprite_comp"):
                        self.sprite_comp.custom_mask = self.crouch_hitbox
                    if self.rect.height == 60:
                        self.rect.height = 40
                else:
                    if hasattr(self, "sprite_comp"):
                        self.sprite_comp.custom_mask = self.normal_hitbox
                    if self.rect.height == 40:
                        self.rect.height = 60
                self._tbag_toggle_timer += getattr(self, "_tbag_toggle_interval", 0.06)

        if hasattr(self, "_tbag_sequence_timer"):
            self._tbag_sequence_timer -= dt

            if self._tbag_sequence_timer <= 0:
                self._tbag_sequence_index += 1

                if self._tbag_sequence_index < len(self._tbag_pulse_sequence):
                    duration, is_crouch = self._tbag_pulse_sequence[
                        self._tbag_sequence_index
                    ]
                    self._tbag_sequence_timer = duration
                    self.is_crouching = is_crouch
                else:
                    del self._tbag_sequence_timer
                    del self._tbag_sequence_index
                    del self._tbag_pulse_sequence
                    self.is_crouching = False
        elif hasattr(self, "_crouch_pulse_timer"):
            if self._crouch_pulse_timer > 0:
                self._crouch_pulse_timer -= dt
                self.is_crouching = True
            else:
                self.is_crouching = False

        super().update(dt)

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
            self.sprite_comp.mask = self.crouch_hitbox
        else:
            self.animator.set_state("idle")
            self.sprite_comp.mask = self.normal_hitbox

        self.animator.update(dt)

        if self.flash_timer > 0:
            self.shiver_offset.x = (pygame.time.get_ticks() % 10) - 5
            self.sprite_comp.visible = True
        else:
            self.shiver_offset.x = 0
            self.sprite_comp.visible = (
                not self.invulnerable or (pygame.time.get_ticks() // 80) % 2 == 0
            )

        self.sprite_comp.offset.x = self.base_visual_offset.x + self.shiver_offset.x

        if abs(self.movable.velocity.x) < 50:
            cam_x = self.phase.allsprites.offset.x
            self.facing_right = (pygame.mouse.get_pos()[0] + cam_x) > self.rect.centerx
        else:
            self.facing_right = self.movable.velocity.x > 0

        self.sprite_comp.flip_x = not self.facing_right

    def change_skin(self, new_skin: str) -> None:
        """Permet de changer le skin du joueur en cours de jeu."""
        self.skin_variant = new_skin
        self._setup_animations()

    def jeu_gagne(self):
        """Ancienne condition basée sur tbag_nombre.
        Sert pas dans le nouveau système"""
        return False
