import pygame


class MaskFactory:
    """
    Générateur de formes de collision (masques) pour découpler
    la hitbox physique du visuel.
    """

    @staticmethod
    def from_image(image: pygame.Surface) -> pygame.mask.Mask:
        """Crée un masque basé sur la transparence réelle de l'image."""
        return pygame.mask.from_surface(image)

    @staticmethod
    def capsule_mask(width: int, height: int) -> pygame.mask.Mask:
        """
        Crée une forme de gélule (ellipse).
        Idéal pour les personnages pour éviter de 'trébucher' sur les rebords.
        """
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        # On remplit l'ellipse en blanc (opaque) pour le masque
        pygame.draw.ellipse(surface, (255, 255, 255), (0, 0, width, height))
        return pygame.mask.from_surface(surface)

    @staticmethod
    def rect_mask(width: int, height: int) -> pygame.mask.Mask:
        """Crée un masque rectangulaire plein."""
        # Pas besoin de SRCALPHA ici, on veut un bloc plein
        surface = pygame.Surface((width, height))
        surface.fill((255, 255, 255))
        return pygame.mask.from_surface(surface)

    @staticmethod
    def circle_mask(radius: int) -> pygame.mask.Mask:
        """Crée un masque circulaire (utile pour les projectiles ou explosions)."""
        diameter = radius * 2
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(surface, (255, 255, 255), (radius, radius), radius)
        return pygame.mask.from_surface(surface)
