import pygame

import core.configs.settings as stgs


class CameraGroup(pygame.sprite.Group):
    """
    Système de rendu gérant le suivi fluide (Lerp) et le décalage des sprites.
    """

    def __init__(self) -> None:
        super().__init__()
        self.offset = pygame.Vector2()
        self.smoothing = 0.1  # Réactivité de la caméra (basée sur 60 FPS)
        self.min_move_threshold = 0.1  # Seuil pour stopper les micro-vibrations

    def update_camera(self, target: pygame.sprite.Sprite, dt: float) -> None:
        """
        Calcule la position de la caméra vers la cible.
        Ajustement via dt pour que la vitesse soit identique peu importe le framerate.
        """
        target_center = pygame.Vector2(target.rect.center)
        screen_center = pygame.Vector2(stgs.SCREEN_WIDTH // 2, stgs.SCREEN_HEIGHT // 2)
        ideal_offset = target_center - screen_center

        # Normalisation du lissage selon le temps écoulé (delta time)
        lerp_factor = self.smoothing * (dt * 60)

        if lerp_factor >= 1.0:
            self.offset = ideal_offset
        else:
            diff = ideal_offset - self.offset
            # On arrête le mouvement si l'écart est insignifiant (évite les tremblements)
            if diff.length() > self.min_move_threshold:
                self.offset += diff * lerp_factor
            else:
                self.offset = ideal_offset

    def custom_draw(
        self, screen: pygame.Surface, render_offset: pygame.Vector2, debug: bool = False
    ) -> None:
        """
        Gère l'affichage des entités.
        Utilise le composant de rendu dédié ou une méthode de secours classique.
        """
        for sprite in self.sprites():
            # Priorité au composant (supporte les effets de flash et shaders)
            if hasattr(sprite, "sprite_comp"):
                sprite.sprite_comp.draw(screen, render_offset)

                if debug and hasattr(sprite.sprite_comp, "draw_debug"):
                    sprite.sprite_comp.draw_debug(screen, render_offset)

            # Méthode de secours si l'entité n'a pas de composant graphique
            elif hasattr(sprite, "image"):
                draw_pos = sprite.rect.topleft - render_offset
                screen.blit(sprite.image, draw_pos)
