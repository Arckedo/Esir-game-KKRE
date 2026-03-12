import pygame


class MovableComponent:
    """
    Gère la physique, la gravité et les collisions.
    """

    def __init__(self, owner, speed):
        self.owner = owner
        self.max_speed = speed
        self.velocity = pygame.Vector2(0, 0)
        self.pos = pygame.Vector2(self.owner.rect.topleft)

        # Lissage (Lerp) pour l'accélération et le freinage
        self.acceleration_smooth = 0.15
        self.friction_smooth = 0.1

        self.input_dir = pygame.Vector2(0, 0)
        self.gravity = 2000
        self.terminal_velocity = 1000
        self.on_ground = False

    def update(self, dt):
        # 1. On récupère le collider s'il existe
        collider = self.owner.get_component("collision")

        # 2. CALCUL X (Accélération progressive)
        target_vel_x = self.input_dir.x * self.max_speed
        if self.input_dir.x != 0:
            self.velocity.x += (
                target_vel_x - self.velocity.x
            ) * self.acceleration_smooth
        else:
            self.velocity.x += (0 - self.velocity.x) * self.friction_smooth

        # 3. CALCUL Y (Gravité)
        if not self.on_ground:
            self.velocity.y += self.gravity * dt
            if self.velocity.y > self.terminal_velocity:
                self.velocity.y = self.terminal_velocity

        # 4. MOUVEMENT ET COLLISIONS

        # --- AXE X (Horizontal) ---
        new_x = self.pos.x + self.velocity.x * dt
        test_rect = self.owner.rect.copy()
        test_rect.x = round(new_x)

        if collider and collider.check_solids(test_rect):
            # Logique de 'Step Up' : on tente de "monter" sur l'obstacle
            step_passed = False
            max_step_height = 8  # Hauteur max franchissable sans sauter

            for s in range(1, max_step_height + 1):
                step_test_rect = test_rect.copy()
                step_test_rect.y -= s  # On décale le test vers le haut

                if not collider.check_solids(step_test_rect):
                    # Ça passe ! On valide le mouvement et on soulève le perso
                    self.pos.x = new_x
                    self.pos.y -= s
                    step_passed = True
                    break

            if not step_passed:
                # C'est vraiment un mur, on stoppe net
                self.velocity.x = 0
        else:
            self.pos.x = new_x

        # --- AXE Y (Vertical) ---
        self.on_ground = False
        new_y = self.pos.y + self.velocity.y * dt
        test_rect_y = self.owner.rect.copy()

        # On utilise la nouvelle position X pour tester la collision Y
        test_rect_y.topleft = (round(self.pos.x), round(new_y))

        if collider and collider.check_solids(test_rect_y):
            # Collision détectée (Sol ou Plafond)
            if self.velocity.y > 0:
                self.on_ground = True
            self.velocity.y = 0
        else:
            self.pos.y = new_y

        # 5. SYNCHRONISATION FINALE
        # On arrondit pour éviter les tremblements de sprites (sub-pixel jitter)
        self.owner.rect.topleft = (round(self.pos.x), round(self.pos.y))

        # 6. RESET DES INPUTS
        self.input_dir.update(0, 0)

    def jump(self, force):
        """Propulse le joueur vers le haut s'il est au sol."""
        if self.on_ground:
            self.velocity.y = -force
            self.on_ground = False
