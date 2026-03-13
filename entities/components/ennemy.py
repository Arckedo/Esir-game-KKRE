import math

import pygame


class EnemyProjectile(pygame.sprite.Sprite):
    """
    Projectile standard tiré par les ennemis.
    Gère sa propre physique et permet de choisir si les murs l'arrêtent ou non.
    """

    def __init__(self, x, y, angle, phase, speed=3, collide_with_walls=True):
        super().__init__()
        self.phase = phase
        self.collide_with_walls = collide_with_walls  # Le petit levier pour choisir !

        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 0, 0), (5, 5), 5)
        self.rect = self.image.get_rect(center=(x, y))

        # Vecteur de direction basé sur l'angle de tir
        self.direction = pygame.Vector2(math.cos(angle), math.sin(angle))
        self.speed = speed
        self.pos = pygame.Vector2(x, y)

    def update(self, dt):
        # Mouvement indépendant du framerate (toujours fluide !)
        self.pos += self.direction * self.speed * dt * 60
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # --- GESTION DES COLLISIONS AVEC LE DÉCOR ---
        # On ne vérifie que si le projectile n'est pas "fantôme" (traverse les murs)
        if self.collide_with_walls:
            # 1. Collision avec le masque du niveau (précision au pixel)
            if hasattr(self.phase, "level_mask"):
                try:
                    if self.phase.level_mask.get_at((int(self.pos.x), int(self.pos.y))):
                        self.kill()  # Paf le mur !
                        return
                except IndexError:
                    # Hop, on est sorti des limites de la map, on nettoie
                    self.kill()
                    return

            # 2. Collision avec les objets solides (si tu as des blocs destructibles par ex)
            if pygame.sprite.spritecollideany(self, self.phase.solids):
                self.kill()
                return

        # 3. Collision avec le joueur (Vérification par Rect, c'est du rapide)
        if self.rect.colliderect(self.phase.player.rect):
            self.deal_damage(self.phase.player)

        # Filet de sécurité : si la balle part dans l'infini, on la supprime
        if self.pos.length_squared() > 10_000_000:
            self.kill()

    def deal_damage(self, player):
        """On inflige les dégâts et on fait disparaître la balle."""
        if player.take_damage(1, source_pos=self.pos):
            self.kill()


# --- COMPOSANTS DE COMPORTEMENT ---


class FloatingComponent:
    """Ajoute une oscillation verticale sinusoïdale à l'entité."""

    def __init__(self, parent, amplitude=15, speed=3):
        self.parent = parent
        self.amplitude = amplitude
        self.speed = speed
        self.timer = 0
        self.base_y = parent.rect.centery

    def update(self, dt):
        self.timer += dt * self.speed
        self.parent.rect.centery = self.base_y + math.sin(self.timer) * self.amplitude


class CircularShootComponent:
    """Gère un pattern de tir circulaire à intervalle régulier."""

    def __init__(self, parent, phase, cooldown=2.0, bullet_count=12, walls_block=True):
        self.parent = parent
        self.phase = phase
        self.cooldown = cooldown
        self.last_shot = 0
        self.bullet_count = bullet_count
        self.walls_block = walls_block

    def update(self, dt):
        current_time = pygame.time.get_ticks() / 1000
        if current_time - self.last_shot > self.cooldown:
            self.shoot()
            self.last_shot = current_time

    def shoot(self):
        """Instancie une salve de projectiles à 360 degrés."""
        for i in range(self.bullet_count):
            angle = i * (2 * math.pi / self.bullet_count)

            proj = EnemyProjectile(
                self.parent.rect.centerx,
                self.parent.rect.centery,
                angle,
                self.phase,
                collide_with_walls=self.walls_block,
            )

            self.phase.allsprites.add(proj)
            self.phase.enemy_projectiles.add(proj)
