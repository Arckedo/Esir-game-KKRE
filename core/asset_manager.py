import os

import pygame


class AssetManager:
    """
    Gestionnaire centralisé des ressources pour optimiser la mémoire et les accès disque.
    """

    _images: dict[str, pygame.Surface] = {}

    @classmethod
    def get_image(cls, name: str, has_alpha: bool = True) -> pygame.Surface | None:
        """
        Récupère une image, la charge si nécessaire et l'optimise pour le rendu.
        """
        if name not in cls._images:
            # Construction dynamique du chemin
            path = os.path.join("assets", "images", f"{name}.png")

            if not os.path.exists(path):
                print(f"⚠️ Ressource manquante : {path}")
                return None

            try:
                # Chargement initial
                surface = pygame.image.load(path)

                # Optimisation Pygame (indispensable pour les performances)
                if has_alpha:
                    cls._images[name] = surface.convert_alpha()
                else:
                    cls._images[name] = surface.convert()

            except pygame.error as e:
                print(f"❌ Erreur Pygame lors du chargement de {name} : {e}")
                return None

        return cls._images[name]

    @classmethod
    def get_spritesheet(
        cls, name: str, width: int, height: int
    ) -> list[pygame.Surface]:
        """
        Découpe une planche de sprites (spritesheet) en une liste de frames.
        """
        sheet = cls.get_image(name)
        if not sheet:
            return []

        frames = []
        sheet_w, sheet_h = sheet.get_size()

        # Parcours de la planche par ligne puis par colonne
        for y in range(0, sheet_h - height + 1, height):
            for x in range(0, sheet_w - width + 1, width):
                rect = pygame.Rect(x, y, width, height)
                # .copy() permet de libérer la grosse planche de la mémoire si besoin
                frames.append(sheet.subsurface(rect).copy())

        return frames

    @staticmethod
    def create_animation_data(frames: list, duration: float | list) -> list:
        """
        Associe chaque frame à une durée d'affichage.
        """
        if isinstance(duration, (int, float)):
            return [(f, duration) for f in frames]
        return list(zip(frames, duration))
