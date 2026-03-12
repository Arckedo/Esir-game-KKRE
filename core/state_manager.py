class StateManager:
    """
    Gère la pile des états du jeu.
    Permet de superposer des états (ex : Menu sur le Gameplay)
    Ref: https://gameprogrammingpatterns.com/state.html
    """

    def __init__(self):
        """Initialisation une pile d'états vide."""
        self.states = []

    def push(self, state):
        """Ajoute un nouvel état au sommet de la pile et le rend actif.

        Args:
            state: L'instance de la phase à ajouter (ex: TopDownPhase())
        """
        self.states.append(state)

    def pop(self):
        """
        Retire l'état actuel pour revenir à l'état précédent.
        Garantit qu'il reste tjrs au moins un état dans la pile
        """
        if len(self.states) > 1:
            self.states.pop()

    def current(self):
        """
        Récupère l'état actif (celui au sommet de la pile).

        Returns:
            L'état actuel ou None si il n'y a rien dans la pile.
        """
        return self.states[-1] if self.states else None
