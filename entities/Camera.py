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
        self.zoom = 1.0
        self.zoom_smoothing = 0.12
        self.zoom_min = 0.75
        self.zoom_max = 1.8
        self.zoom_size_min = 220
        self.zoom_size_max = 1200

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

        # En mode mono-cible, retour progressif au zoom neutre.
        zoom_lerp = min(1.0, self.zoom_smoothing * (dt * 60))
        self.zoom += (1.0 - self.zoom) * zoom_lerp


    def update_camera_multi(self, targets: list[pygame.sprite.Sprite], dt: float) -> None:
        """
        Ajuste la caméra pour garder exactement deux joueurs visibles avec des marges,
        puis applique un lissage (Lerp) sur la position et le zoom.
        """
        # On extrait directement les positions des deux joueurs
        p1_rect, p2_rect = targets[0].rect, targets[1].rect

        # Encadrement entre les deux joueurs
        min_x = min(p1_rect.left, p2_rect.left)
        max_x = max(p1_rect.right, p2_rect.right)
        min_y = min(p1_rect.top, p2_rect.top)
        max_y = max(p1_rect.bottom, p2_rect.bottom)

        # Zoom dynamique selon la distance maximale entre les deux joueurs
        taille_box = max(max_x - min_x, max_y - min_y)

        # Interpolation du zoom (0.0 = proche, 1.0 = éloigné)
        size_span = max(1, self.zoom_size_max - self.zoom_size_min)
        t = max(0.0, min(1.0, (taille_box - self.zoom_size_min) / size_span))
        zoom_ideal = self.zoom_max - t*(self.zoom_max - self.zoom_min) #formule mathématique compliquée de fou furieux, en gros plus la box est grande, plus le zoom est petit, et inversement.

        #Dimensions de l'écran et marges fixes (ça change pas)
        screen_w, screen_h = stgs.SCREEN_WIDTH, stgs.SCREEN_HEIGHT
        margin_x, margin_y = 300, 180

        #Centre entre les deux joueurs
        centre_x = (min_x + max_x)*0.5
        centre_y = (min_y + max_y)*0.5
        ideal_offset = pygame.Vector2(centre_x - screen_w * 0.5, centre_y - screen_h * 0.5)

        # Ajustement de l'offset pour respecter les marges de sécurité si l'espace le permet
        if (max_x - min_x) <= (screen_w - 2 * margin_x):
            ideal_offset.x = max(max_x - (screen_w - margin_x), min(ideal_offset.x, min_x - margin_x))
            
        if (max_y - min_y) <= (screen_h - 2 * margin_y):
            ideal_offset.y = max(max_y - (screen_h - margin_y), min(ideal_offset.y, min_y - margin_y))

        #Applique le lissage au lieu de déplacer direct
        lerp_factor = self.smoothing * (dt * 60)
        if lerp_factor >= 1.0:
            self.offset = ideal_offset
        else:
            diff = ideal_offset - self.offset
            if diff.length() > self.min_move_threshold:
                self.offset += diff * lerp_factor
            else:
                self.offset = ideal_offset

        #Lissage du zoom
        zoom_lerp = min(1.0, self.zoom_smoothing * (dt * 60))
        self.zoom += (zoom_ideal - self.zoom) * zoom_lerp


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
