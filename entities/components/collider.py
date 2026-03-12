class ColliderComponent:
    def __init__(self, owner, world_group):
        self.owner = owner
        self.world_group = world_group  # Groupe contenant les murs/sol

    def check_collisions(self, next_pos):
        """
        Vérifie si la position future 'next_pos' (pygame.Rect)
        provoque une collision avec le décor.
        """
        for obstacle in self.world_group:
            # Calcul de l'offset entre le joueur et l'obstacle
            offset_x = obstacle.rect.x - next_pos.x
            offset_y = obstacle.rect.y - next_pos.y

            # Si les masques se chevauchent à cet endroit
            if self.owner.mask.overlap(obstacle.mask, (offset_x, offset_y)):
                return obstacle
        return None
