import pygame

from core.asset_manager import AssetManager


class Cursor:
    """
    Gère l'affichage d'un curseur personnalisé remplaçant la souris système.
    """

    def __init__(self, image_name: str) -> None:
        self.image = AssetManager.get_image(image_name)
        self.rect = self.image.get_rect()

        # Désactive le curseur système pour éviter les doublons visuels
        pygame.mouse.set_visible(False)

    def update(self) -> None:
        """Met à jour la position du curseur sur les coordonnées de la souris."""
        self.rect.center = pygame.mouse.get_pos()

    def change_style(self, new_image_name: str) -> None:
        """Change l'apparence du curseur tout en conservant son centrage."""
        old_center = self.rect.center
        self.image = AssetManager.get_image(new_image_name)
        # On recrée le rect mais on lui redonne l'ancienne position immédiatement
        self.rect = self.image.get_rect(center=old_center)

    def draw(self, screen: pygame.Surface) -> None:
        """
        Affiche le curseur.
        Note : À appeler en dernier dans la boucle de rendu pour qu'il soit au-dessus de tout.
        """
        screen.blit(self.image, self.rect)
