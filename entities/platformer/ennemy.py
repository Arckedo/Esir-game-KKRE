import pygame

from entities.base_entity import BaseEntity
from entities.components.ennemy import CircularShootComponent, FloatingComponent


class CasterEnemy(BaseEntity):
    """
    Ennemi statique utilisant des composants pour le mouvement (lévitation)
    et l'attaque (tir circulaire).
    """

    def __init__(self, x, y, phase):
        super().__init__(x, y)
        self.phase = phase

        # Placeholder visuel : mage sphérique
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (250, 0, 0), (20, 20), 20)
        self.rect = self.image.get_rect(center=(x, y))

        # Initialisation des comportements spécialisés
        # FloatingComponent : gère l'oscillation verticale (Y)
        self.add_component("floating", FloatingComponent(self, amplitude=20, speed=2))

        # CircularShootComponent : gère le pattern de tir et le cooldown
        self.add_component(
            "shooter",
            CircularShootComponent(self, phase, bullet_count=10, walls_block=False),
        )

    def update(self, dt: float) -> None:
        """
        L'update de BaseEntity se charge de mettre à jour chaque composant.
        On peut ajouter ici une logique de détection de portée si besoin.
        """
        super().update(dt)
