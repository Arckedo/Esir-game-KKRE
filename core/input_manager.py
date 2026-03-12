import pygame


class InputManager:
    """
    Interprète les entrées physiques en actions logiques.
    Permet de séparer la configuration des touches de l'exécution des actions.
    Ref: https://gameprogrammingpatterns.com/command.html#configuring-input
    """

    def __init__(self, key_map: dict):
        """
        Initialise le gestionnaire avec un dictionnaire.

        Args:
            key_map: Dictionnaire associant un nom d'action a une touche pygame.
                     ex : {"jump": pygame.K_SPACE}.
        """
        self.key_map = key_map
        self.MOUSE_LEFT = "MOUSE_LEFT"

    def get_commands(self, events):
        """
        Détecte les pressions de touches uniques (événements de type KEYDOWN).
        C'est à dire que ca ne détecte que 1 fois si on appuie dessus, pas à chaque frame.
        Idéal pour des actions comme 'Sauter' ou 'Ouvrir Inventaire'.

        Args:
            events: La liste des événements récupérés par pygame.event.get().

        Returns:
            list[str]: Une liste contenant les noms des actions déclenchées à cette frame
                       (ex: ["jump", "inventory"]).
        """
        active_actions = []
        for event in events:
            # 1. Gestion CLAVIER (KEYDOWN)
            if event.type == pygame.KEYDOWN:
                for action_name, key in self.key_map.items():
                    if event.key == key:
                        active_actions.append(action_name)

            # 2. Gestion SOURIS (Appui unique)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 1 est le clic gauche
                    for action_name, key in self.key_map.items():
                        if key == self.MOUSE_LEFT:
                            active_actions.append(action_name)
        return active_actions

    def get_continuous_commands(self):
        """
        Détecte les touches maintenues enfoncées.
        Idéal pour des déplacements fluides (ex : courir d'un côté).

        Returns:
            list[str]: Une liste des actions dont la touche est pressée
                       (ex: ["move_left", "sprint"]).
        """
        active_actions = []

        # État du clavier
        keys_pressed = pygame.key.get_pressed()
        # État de la souris (bouton gauche, milieu, droit)
        mouse_pressed = pygame.mouse.get_pressed()

        for action_name, key in self.key_map.items():
            # Si c'est une touche clavier standard
            if isinstance(key, int) and key != -1:
                if keys_pressed[key]:
                    active_actions.append(action_name)
            # Si c'est notre constante de souris
            elif key == self.MOUSE_LEFT:
                if mouse_pressed[0]:  # 0 est l'index pour le clic gauche
                    active_actions.append(action_name)

        return active_actions

    def call_commands(self, active_actions, action_dict, receiver):
        """
        Transforme les noms d'actions en objets Command et les exécute sur une cible.

        Args:
            active_actions: Liste des chaînes de caractères (ex: ['jump','left'])
            action_dict: Dictionnaire faisant le lien entre le nom et l'objet Command
            receiver: L'entité qui doit subir l'action (ex: 'le Player')
        """
        for action_name in active_actions:
            command = action_dict.get(action_name)
            if command:
                command.execute(receiver)
