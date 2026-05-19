import pygame


class InputManager:
    """
    Interprète les entrées physiques en actions logiques.
    Permet de séparer la configuration des touches de l'exécution des actions.
    Ref: https://gameprogrammingpatterns.com/command.html#configuring-input
    """

    def __init__(self, key_map: dict, joystick_index: int = 0):
        """
        Initialise le gestionnaire avec un dictionnaire.

        Args:
            key_map: Dictionnaire associant un nom d'action a une touche pygame.
                     ex : {"jump": pygame.K_SPACE}.
        """
        self.key_map = key_map
        self.joystick_index = joystick_index
        self.MOUSE_LEFT = "MOUSE_LEFT"
        self.MOUSE_RIGHT = "MOUSE_RIGHT"
        self.MOUSE_MIDDLE = "MOUSE_MIDDLE"

        # 1/4 de l'inclinaison du stick pour éviter les activations accidentelles
        self.AXIS_DEADZONE = 0.25
        self._axis_up_was_active = False
        self.debug_button = Button(
            100, 200, pygame.image.load("assets/images/debug.png").convert_alpha(), 0.1
        )

    def _binding_matches_event(self, binding, event) -> bool:
        """Teste si un binding clavier/souris/manette correspond à un événement."""
        if isinstance(binding, (list, tuple, set)):
            return any(self._binding_matches_event(item, event) for item in binding)

        if event.type == pygame.KEYDOWN and isinstance(binding, int):
            return event.key == binding

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return binding == self.MOUSE_LEFT
            if event.button == 2:
                return binding == self.MOUSE_MIDDLE
            if event.button == 3:
                return binding == self.MOUSE_RIGHT

        if (
            event.type == pygame.JOYBUTTONDOWN
            and isinstance(binding, str)
            and binding.startswith("JOY_")
        ):
            button_index = int(binding.split("_")[1])
            return event.button == button_index

        return False

    def get_joystick(self):
        """Retourne la manette configurée pour ce manager, sinon None."""
        if self.joystick_index < 0:
            return None
        # vérification que la manette existe toujours avec get_count(nombre de manette connectée)
        if pygame.joystick.get_count() <= self.joystick_index:
            return None
        # création de l'objet joystick pour la manette avec l'index (0 pour la première manette, 1 pour la deuxième)
        joystick = pygame.joystick.Joystick(self.joystick_index)
        # vérification que la manette est initialisée, sinon on l'initialise pour pouvoir l'utiliser
        if not joystick.get_init():
            joystick.init()
        return joystick

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
            if event.type == pygame.KEYDOWN:
                print("INPUT KEYDOWN", event.key)
                for action_name, key in self.key_map.items():
                    # Gère les listes de bindings (ex: crouch: [K_c, K_LCTRL, ...])
                    if isinstance(key, (list, tuple, set)):
                        if any(event.key == k for k in key if isinstance(k, int)):
                            active_actions.append(action_name)
                            if action_name == "crouch":
                                print("INPUT KEYDOWN => crouch", event.key)
                    elif event.key == key:
                        active_actions.append(action_name)
                        if action_name == "crouch":
                            print("INPUT KEYDOWN => crouch", event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                for action_name, key in self.key_map.items():
                    if isinstance(key, (list, tuple, set)):
                        if any(
                            (event.button == 1 and k == self.MOUSE_LEFT)
                            or (event.button == 2 and k == self.MOUSE_MIDDLE)
                            or (event.button == 3 and k == self.MOUSE_RIGHT)
                            for k in key
                        ):
                            active_actions.append(action_name)
                    else:
                        if event.button == 1 and key == self.MOUSE_LEFT:
                            active_actions.append(action_name)
                        elif event.button == 2 and key == self.MOUSE_MIDDLE:
                            active_actions.append(action_name)
                        elif event.button == 3 and key == self.MOUSE_RIGHT:
                            active_actions.append(action_name)

            # 3. Gestion MANETTE (JOYBUTTONDOWN)
            elif event.type == pygame.JOYBUTTONDOWN:
                print("JOYBUTTONDOWN", event.button)
                joystick = self.get_joystick()
                if joystick is not None and event.joy == joystick.get_instance_id():
                    for action_name, key in self.key_map.items():
                        if isinstance(key, str) and key.startswith("JOY_"):
                            button_index = int(key.split("_")[1])
                            if event.button == button_index:
                                active_actions.append(action_name)

        # Stick haut en appui unique (désactivé pour le moment)
        # joystick = self.get_joystick()
        # if joystick is not None:

        #    axis_y = joystick.get_axis(1)
        #    axis_up_active = axis_y < -self.AXIS_DEADZONE
        #    if axis_up_active and not self._axis_up_was_active and "top" in self.key_map:
        #        active_actions.append("top")
        #    self._axis_up_was_active = axis_up_active
        # else:
        #    self._axis_up_was_active = False
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
                continue

            # Si c'est une souris
            if key == self.MOUSE_LEFT:
                if mouse_pressed[0]:
                    active_actions.append(action_name)
                continue

            if key == self.MOUSE_MIDDLE:
                if mouse_pressed[1]:
                    active_actions.append(action_name)
                continue

            if key == self.MOUSE_RIGHT:
                if mouse_pressed[2]:
                    active_actions.append(action_name)
                continue

            # Multi-bindings (ex: crouch: [K_c, K_LCTRL, "MOUSE_RIGHT"])
            if isinstance(key, (list, tuple, set)):
                if any(
                    (isinstance(k, int) and k != -1 and keys_pressed[k])
                    or (k == self.MOUSE_LEFT and mouse_pressed[0])
                    or (k == self.MOUSE_MIDDLE and mouse_pressed[1])
                    or (k == self.MOUSE_RIGHT and mouse_pressed[2])
                    for k in key
                ):
                    active_actions.append(action_name)

        # Gestion du mouvement du stick gauche (manette 0) avec deadzone.
        joystick = self.get_joystick()
        if joystick is not None:
            axis_x = joystick.get_axis(0)
            axis_y = joystick.get_axis(1)

            if (
                axis_x < -self.AXIS_DEADZONE
                and "left" in self.key_map
                and "left" not in active_actions
            ):
                active_actions.append("left")
            elif (
                axis_x > self.AXIS_DEADZONE
                and "right" in self.key_map
                and "right" not in active_actions
            ):
                active_actions.append("right")

            if (
                axis_y < -self.AXIS_DEADZONE
                and "top" in self.key_map
                and "top" not in active_actions
            ):
                active_actions.append("top")
            elif (
                axis_y > self.AXIS_DEADZONE
                and "down" in self.key_map
                and "down" not in active_actions
            ):
                active_actions.append("down")

            # Gestion des boutons manette (appui unique / edge detection)
            # get_button() renvoie True tant que le bouton est maintenu.
            # On déclenche donc uniquement sur le front montant (release -> press).
            if not hasattr(self, "_joystick_button_was_down"):
                self._joystick_button_was_down = {}

            for action_name, key in self.key_map.items():
                if isinstance(key, str) and key.startswith("JOY_"):
                    button_index = int(key.split("_")[1])

                    is_down = joystick.get_button(button_index)
                    was_down = self._joystick_button_was_down.get(
                        (self.joystick_index, button_index), False
                    )

                    # Front montant
                    if is_down and not was_down and action_name not in active_actions:
                        # Évite que les boutons manette déclenchent en continu des actions
                        # qui sont déjà traitées à part (ex: top_manette via get_commands).
                        if action_name != "top_manette":
                            active_actions.append(action_name)

                    self._joystick_button_was_down[
                        (self.joystick_index, button_index)
                    ] = is_down

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


class Button:
    def __init__(self, x, y, image, scale):
        self.image = image
        self.scale = scale
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        return True

    def is_pressed(self):
        return True
