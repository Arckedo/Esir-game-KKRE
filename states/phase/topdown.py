import pygame

from core.configs.registry.commands import SYSTEM_COMMANDS, TD_MOVE_COMMANDS
from core.configs.registry.inputmap import TOPDOWN_PHASE_KEYS
from core.engine import GameState
from core.input_manager import InputManager
from entities.platformer.player import PlayerTopDown


class TopDownPhase(GameState):
    """
    Phase de jeu en vue de dessus (Top-Down).
    Gère l'instanciation du joueur, le mapping des commandes et les mises à jour.
    """

    def __init__(self):
        """Initialisation des entités et des contrôles de la phase avec les 3 étapes (INPUT,SYSTEME,ENTITE ET RENDU)."""

        # 1. GESTION DES INPUTS (Configuration des contrôles)

        # Gestionnaire d'input spécifique à cette phase
        self.input_manager = InputManager(TOPDOWN_PHASE_KEYS)
        # Dictionnaires liant les actions aux objets Command
        self.player_actions = TD_MOVE_COMMANDS
        self.system_actions = SYSTEM_COMMANDS

        # 2. SYSTEMES DE LA PHASE (Caméra, UI et physique)

        # Y'a rien pour l'instant

        # 3. ENTITES ET RENDU (Joueurs, PNJ, Groupes de sprites)

        # Initialitation du joueur à une position exacte.
        self.player = PlayerTopDown(13 * 32, 30 * 32)
        # Groupe de rendu pour optimiser l'affichage des sprites
        self.allsprites = pygame.sprite.Group()
        self.allsprites.add(self.player)

    # --- MÉTHODE DE BOUCLE DE JEU (UPDATE) ---
    # Appelée à chaque frame par la Phase

    def handle_events(self, events, game):
        """
        Gère les événements système (clic unique, menus, quitter,...).
        Envoie les commandes à l'input manager de la phase, avec "game" comme argument.
        """
        system_calls = self.input_manager.get_commands(events)
        self.input_manager.call_commands(system_calls, self.system_actions, game)

    def update(self, game):
        """
        Gère la logique continue (déplacements, collisions,...).
        1.Envoie les commandes continues à l'input manager de la phase.
        2.Puis lance la logique des entitées dans le update.
        """
        # Récupération des touches maintenues (Z,Q,S,D,...)
        move_calls = self.input_manager.get_continuous_commands()
        self.input_manager.call_commands(move_calls, self.player_actions, self.player)

        # 2. Mise à jour de la physique du joueur basée sur le Delta Time
        self.player.update(game.dt)

    def draw(self, screen):
        """Rendu graphique de la phase."""
        screen.fill((128, 128, 128))
        self.allsprites.draw(screen)
