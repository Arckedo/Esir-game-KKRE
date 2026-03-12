import math

import pygame


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos):
        super().__init__()
        self.speed = 1200  # Un peu plus rapide pour le feeling

        # 1. Position et Direction
        self.pos = pygame.Vector2(x, y)
        self.start_pos = pygame.Vector2(x, y)  # On mémorise d'où elle part

        target = pygame.Vector2(target_pos)
        if target == self.pos:
            self.direction = pygame.Vector2(1, 0)
        else:
            self.direction = (target - self.pos).normalize()

        # 2. Visuel
        self.image = pygame.Surface((12, 6), pygame.SRCALPHA)
        self.image.fill((255, 200, 0))
        angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))
        self.image = pygame.transform.rotate(self.image, angle)

        self.rect = self.image.get_rect(center=(x, y))

        # 3. Paramètre de portée
        self.max_range = 2000  # La balle meurt après 1500 pixels de voyage

    def update(self, dt):
        # Déplacement
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

        # --- LOGIQUE DE DESTRUCTION ---

        # A. Si la balle dépasse sa portée maximale
        # (C'est beaucoup mieux que des coordonnées X/Y fixes !)
        if self.pos.distance_to(self.start_pos) > self.max_range:
            self.kill()

        # B. Optionnel : Si elle touche un mur (solids)
        # Il faut que tu passes 'phase' à ta balle ou que tu y accèdes
        # if pygame.sprite.spritecollideany(self, self.phase.solids):
        #     self.kill()
