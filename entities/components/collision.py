import pygame


class CollisionComponent:
    """
    Gère les collisions précises par masque entre une entité et le décor.
    """

    def __init__(self, owner):
        self.owner = owner
        # On récupère la phase une seule fois pour éviter les vérifications répétitives
        self.phase = getattr(owner, "phase", None)

    def check_solids(self, test_rect: pygame.Rect) -> bool:
        """
        Vérifie si le masque de l'entité touche le masque de collision du niveau.
        """
        # Si la phase n'est pas encore liée, on tente de la récupérer
        if not self.phase:
            self.phase = getattr(self.owner, "phase", None)

        if self.phase and hasattr(self.phase, "level_mask"):
            # On utilise le masque actuel de l'owner (joueur ou ennemi)
            mask = self.owner.mask

            # Calcul du décalage (offset) : où se trouve le masque par rapport au monde
            # On aligne le coin haut-gauche du masque avec celui du rect de test
            offset_x = test_rect.x
            offset_y = test_rect.y

            # Test d'intersection entre le masque global et le masque de l'entité
            if self.phase.level_mask.overlap(mask, (offset_x, offset_y)):
                return True

        return False
