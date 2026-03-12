from abc import ABC, abstractmethod

import pygame


class GameState(ABC):
    """
    Interface pour tous les états du jeu,
    Garantit que chaque phase est les méhodes requises par le main.
    Ref: https://gameprogrammingpatterns.com/state.html#a-state-interface
    """

    @abstractmethod
    def handle_events(self, events, game) -> None:
        """Traite les entrées utilisateurs (ex : clavier + souris)"""
        pass

    @abstractmethod
    def update(self, game) -> None:
        """Gère la logique et la physique de l'état"""
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Effectue le rendu graphique de l'état sur la Surface"""
        pass


class Command(ABC):
    """
    Interface pour le pattern Command.
    Permet de découpler l'input (touche) de l'action (saut, tir, ...).
    Ref: https://gameprogrammingpatterns.com/command.html#configuring-input
    """

    def execute(self, target) -> None:
        """Exécute l'action sur une entité cible (ex: le player)"""
