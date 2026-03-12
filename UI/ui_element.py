import pygame

from core.asset_manager import AssetManager


class UIHealthBar:
    """
    Interface de santé fixe à l'écran.
    Gère l'affichage du portrait (cœur), du panneau de fond et de la barre de vie.
    """

    def __init__(self, player):
        self.player = player

        # --- Paramètres de mise en page ---
        self.bg_ui_scale = 3.0
        self.content_scale = 1.0

        self.left_margin = 10  # Décalage horizontal depuis le bord
        self.panel_y = 5  # Décalage vertical depuis le haut

        # Ajustements précis du contenu à l'intérieur du parchemin/panneau
        self.offset_x = 78
        self.offset_y = -7
        self.inner_spacing = 10

        # --- Chargement des ressources ---
        bar_sheet = AssetManager.get_image("ui/health_bar")
        empty_sheet = AssetManager.get_image("ui/empty_bar")
        royal_heart_sheet = AssetManager.get_image("ui/royal_heart")
        panel_base = AssetManager.get_image("ui/healthback")

        # Sécurité : on arrête tout si une ressource manque
        if any(
            img is None
            for img in [bar_sheet, empty_sheet, royal_heart_sheet, panel_base]
        ):
            return

        # Pré-optimisation des images
        self.panel_img = pygame.transform.scale_by(panel_base, self.bg_ui_scale)

        # Découpe et mise à l'échelle de la barre (16px de haut par défaut)
        bar_w = bar_sheet.get_width()
        rect = pygame.Rect(0, 0, bar_w, 16)
        self.bg_img = pygame.transform.scale_by(
            empty_sheet.subsurface(rect), self.content_scale
        )
        self.fill_img = pygame.transform.scale_by(
            bar_sheet.subsurface(rect), self.content_scale
        )

        # Découpe des états du cœur (3 frames : Sain, Blessé, Critique)
        self.heart_states = []
        fw = royal_heart_sheet.get_width() // 3
        fh = royal_heart_sheet.get_height()
        for i in range(3):
            sub = royal_heart_sheet.subsurface(pygame.Rect(i * fw, 0, fw, fh))
            self.heart_states.append(pygame.transform.scale_by(sub, self.content_scale))

    def draw(self, screen: pygame.Surface):
        """Affiche l'interface de vie en coordonnées écran (pas de caméra)."""
        if not hasattr(self, "bg_img"):
            return

        # Récupération des stats du joueur
        hp = getattr(self.player, "hp", 6)
        max_hp = getattr(self.player, "max_hp", 6)
        ratio = max(0.0, min(1.0, hp / max_hp))

        # Sélection de l'icône selon la santé restante
        if ratio > 0.6:
            heart_img = self.heart_states[0]  # Normal
        elif ratio > 0.2:
            heart_img = self.heart_states[1]  # Blessé
        else:
            heart_img = self.heart_states[2]  # Danger

        # --- Calcul des positions relatives ---
        # Le panneau sert de point de référence (0,0 de l'UI)
        px, py = self.left_margin, self.panel_y

        # Centrage vertical du contenu dans le panneau
        content_y = py + (self.panel_img.get_height() // 2) + self.offset_y

        # Positionnement horizontal en chaîne : Coeur -> Spacing -> Barre
        hx = px + self.offset_x
        hy = content_y - (heart_img.get_height() // 2)

        bx = hx + heart_img.get_width() + self.inner_spacing
        by = content_y - (self.bg_img.get_height() // 2)

        # --- Rendu final ---
        screen.blit(self.panel_img, (px, py))
        screen.blit(heart_img, (hx, hy))
        screen.blit(self.bg_img, (bx, by))

        # Rendu de la partie pleine avec un 'area' pour l'effet de jauge
        visible_w = int(self.fill_img.get_width() * ratio)
        if visible_w > 0:
            clip = pygame.Rect(0, 0, visible_w, self.fill_img.get_height())
            screen.blit(self.fill_img, (bx, by), area=clip)
