class Animator:
    """
    Gère les cycles d'animations basés sur le temps (Delta Time).
    Permet de basculer entre différents états (idle, run, etc.).
    """

    def __init__(self, owner, animations, default_state="idle"):
        self.owner = owner
        # Format attendu : {"nom_etat": [(Surface, duree_frame), ...]}
        self.animations = animations
        self.state = default_state
        self.frame_index = 0
        self.timer = 0.0

        # Initialisation de la première image
        if self.state in self.animations:
            self.owner.image = self.animations[self.state][0][0]

    def update(self, dt: float):
        """Met à jour le timer et change de frame si nécessaire."""
        if self.state not in self.animations:
            return

        frames = self.animations[self.state]
        self.timer += dt

        # On récupère la durée de la frame actuelle
        current_frame_duration = frames[self.frame_index][1]

        if self.timer >= current_frame_duration:
            # On soustrait la durée au lieu de remettre à zéro pour garder la précision
            # si le dt est très grand (lag)
            self.timer -= current_frame_duration

            self.frame_index = (self.frame_index + 1) % len(frames)
            self.owner.image = frames[self.frame_index][0]

    def set_state(self, new_state: str):
        """Bascule vers une nouvelle animation si elle est différente de l'actuelle."""
        if self.state == new_state or new_state not in self.animations:
            return

        self.state = new_state
        self.frame_index = 0
        self.timer = 0.0
        # Mise à jour visuelle immédiate pour éviter un "glitch" d'une frame
        self.owner.image = self.animations[self.state][0][0]
