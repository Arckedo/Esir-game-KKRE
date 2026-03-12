import pygame
from pygame.sprite import Sprite


class BaseEntity(Sprite):
    """
    Classe parente de toutes les entités du jeu.
    Gère le cycle de vie des composants (Update) et l'intégration avec Pygame.
    """

    def __init__(self, x, y):
        super().__init__()
        # Positionnement de base obligatoire pour Pygame
        self.rect = pygame.Rect(x, y, 0, 0)

        # Dictionnaire des composants : { "animator": obj, "collider": obj }
        self.components = {}

    def add_component(self, name, component):
        """Ajoute un module logique à l'entité"""
        self.components[name] = component
        return component

    def get_component(self, name):
        """Récupère un composant spécifique"""
        return self.components.get(name)

    def update(self, dt):
        """Met à jour tous les composants attachés à l'entitée."""
        for component in self.components.values():
            if hasattr(component, "update"):
                component.update(dt)
