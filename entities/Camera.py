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


    def update_camera_multi(
        self,
        targets: list[pygame.sprite.Sprite],
        dt: float,
        margin_x: int = 300,
        margin_y: int = 180,
        viewport_size: tuple[int, int] | None = None,
    ) -> None:
        """
        Ajuste la caméra pour garder plusieurs cibles visibles avec des marges,
        puis applique le même lissage que la caméra standard.
        """
        valid_targets = [t for t in targets if t is not None and hasattr(t, "rect")]
        if not valid_targets:
            return

        if len(valid_targets) == 1:
            self.update_camera(valid_targets[0], dt)
            return

        min_x = min(t.rect.left for t in valid_targets)
        max_x = max(t.rect.right for t in valid_targets)
        min_y = min(t.rect.top for t in valid_targets)
        max_y = max(t.rect.bottom for t in valid_targets)


        # Zoom dynamique selon l'écart entre les cibles.
        box_width = max_x - min_x
        box_height = max_y - min_y
        box_size = max(box_width, box_height)

        # Interpolation 0 -> 1 selon la taille encadrant les joueurs.
        size_span = max(1, self.zoom_size_max - self.zoom_size_min)
        t = (box_size - self.zoom_size_min) / size_span
        t = max(0.0, min(1.0, t))
        zoom_ideal = self.zoom_max - t * (self.zoom_max - self.zoom_min)


        if viewport_size is None:
            screen_w = stgs.SCREEN_WIDTH
            screen_h = stgs.SCREEN_HEIGHT
        else:
            screen_w, screen_h = viewport_size
        usable_w = max(1, screen_w - 2 * margin_x)
        usable_h = max(1, screen_h - 2 * margin_y)

        center_x = (min_x + max_x) * 0.5
        center_y = (min_y + max_y) * 0.5
        ideal_offset = pygame.Vector2(
            center_x - screen_w * 0.5,
            center_y - screen_h * 0.5,
        )

        # Plage d'offset qui garde les cibles dans les marges, si possible.
        offset_x_min = max_x - (screen_w - margin_x)
        offset_x_max = min_x - margin_x
        offset_y_min = max_y - (screen_h - margin_y)
        offset_y_max = min_y - margin_y

        if (max_x - min_x) <= usable_w:
            ideal_offset.x = max(offset_x_min, min(ideal_offset.x, offset_x_max))
        if (max_y - min_y) <= usable_h:
            ideal_offset.y = max(offset_y_min, min(ideal_offset.y, offset_y_max))

        lerp_factor = self.smoothing * (dt * 60)
        if lerp_factor >= 1.0:
            self.offset = ideal_offset
            return

        diff = ideal_offset - self.offset
        if diff.length() > self.min_move_threshold:
            self.offset += diff * lerp_factor
        else:
            self.offset = ideal_offset

        # Lissage dédié du zoom (plus stable visuellement).
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
