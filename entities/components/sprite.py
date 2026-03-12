import pygame


class SpriteComponent:
    """
    Gère le rendu visuel, les effets de flash (dégâts), le flip et le décalage (offset).
    """

    def __init__(self, owner, image, offset=(0, 0), custom_mask=None):
        self.owner = owner
        self.image = image
        self.flip_x = False
        self.visible = True
        self.offset = pygame.Vector2(offset)

        # On définit le masque de collision (priorité au custom_mask pour les hitboxes précises)
        if custom_mask:
            self.owner.mask = custom_mask
        else:
            self.owner.mask = pygame.mask.from_surface(image)

    def draw(self, screen, camera_offset):
        """Dessine l'image de l'entité avec les effets appliqués."""
        if not self.visible:
            return

        # On récupère l'image actuelle (gérée par l'Animator ou l'image par défaut)
        render_img = getattr(self.owner, "image", self.image)
        flash_timer = getattr(self.owner, "flash_timer", 0)

        if render_img is None:
            return

        # --- GESTION DU FLASH BLANC (FEEDBACK DÉGÂTS) ---
        if flash_timer > 0:
            # On transforme le masque en surface blanche pour la silhouette
            temp_mask = pygame.mask.from_surface(render_img)
            render_img = temp_mask.to_surface(
                setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0)
            )

        # --- GESTION DU FLIP (REGARD GAUCHE/DROITE) ---
        if self.flip_x:
            render_img = pygame.transform.flip(render_img, True, False)

        # --- CALCUL DE LA POSITION FINALE ---
        # Position Rect + Décalage visuel - Position Caméra
        draw_x = self.owner.rect.x + self.offset.x - camera_offset.x
        draw_y = self.owner.rect.y + self.offset.y - camera_offset.y

        screen.blit(render_img, (draw_x, draw_y))

    def draw_debug(self, screen, offset):
        """Affiche les hitboxes et les masques pour le développement."""
        # Dessin du masque en vert transparent
        mask_surf = self.owner.mask.to_surface(
            setcolor=(0, 255, 0, 100), unsetcolor=(0, 0, 0, 0)
        )
        debug_pos = (self.owner.rect.x - offset.x, self.owner.rect.y - offset.y)
        screen.blit(mask_surf, debug_pos)

        # Dessin du rect de collision en rouge
        debug_rect = self.owner.rect.copy()
        debug_rect.x -= offset.x
        debug_rect.y -= offset.y
        pygame.draw.rect(screen, (255, 0, 0), debug_rect, 1)
