import pygame


class ParallaxLayer:
    """Représente une couche unique du décor avec sa propre logique de défilement."""

    def __init__(
        self,
        image: pygame.Surface,
        scroll_speed: float,
        v_speed: float,
        base_y: int,
        auto_speed: float,
    ):
        self.image = image
        self.speed = scroll_speed
        self.v_speed = v_speed
        self.base_y = base_y
        self.auto_speed = auto_speed

        self.width = image.get_width()
        self.auto_offset = 0.0

    def update(self, dt: float = 1.0) -> None:
        """Met à jour l'offset automatique (nuages, eau qui coule, etc.)."""
        self.auto_offset += self.auto_speed

    def draw(self, screen: pygame.Surface, camera_offset: pygame.Vector2) -> None:
        """Dessine la couche en bouclant sur l'axe X pour un effet infini."""
        # Calcul du décalage horizontal (Modulo la largeur pour le bouclage)
        shift_x = (-(camera_offset.x * self.speed) + self.auto_offset) % self.width
        # Calcul du décalage vertical
        shift_y = self.base_y - (camera_offset.y * self.v_speed)

        # On dessine 3 fois pour couvrir l'écran lors du bouclage (Gauche, Centre, Droite)
        # Note : On pourrait optimiser à 2 fois selon la largeur de l'image
        screen.blit(self.image, (shift_x - self.width, shift_y))
        screen.blit(self.image, (shift_x, shift_y))
        screen.blit(self.image, (shift_x + self.width, shift_y))


class ParallaxManager:
    """Gère l'ensemble des couches de fond et leur synchronisation avec la caméra."""

    def __init__(self):
        self.layers: list[ParallaxLayer] = []

        # Setup Debug (Initialisé UNE SEULE FOIS)
        self._debug_font = None
        if pygame.font.get_init():
            self._debug_font = pygame.font.SysFont("Arial", 18)

    def add_layer(
        self,
        image_key: str,
        speed: float,
        v_speed: float = 0.05,
        align_bottom: bool = False,
        auto_speed: float = 0,
    ) -> None:
        """Charge, redimensionne et ajoute une nouvelle couche au parallaxe."""
        from core.asset_manager import AssetManager

        img = AssetManager.get_image(image_key)

        if img is None:
            print(f"Warning: Parallax image '{image_key}' not found.")
            return

        screen_w, screen_h = pygame.display.get_surface().get_size()

        # Redimensionnement intelligent pour couvrir la largeur de l'écran
        if img.get_width() < screen_w:
            ratio = screen_w / img.get_width()
            new_size = (screen_w, int(img.get_height() * ratio))
            img = pygame.transform.scale(img, new_size)

        base_y = screen_h - img.get_height() if align_bottom else 0

        self.layers.append(ParallaxLayer(img, speed, v_speed, base_y, auto_speed))

    def update(self) -> None:
        """Met à jour toutes les couches actives."""
        for layer in self.layers:
            layer.update()

    def draw(
        self, screen: pygame.Surface, camera_offset: pygame.Vector2, debug: bool = False
    ) -> None:
        """Dessine toutes les couches et affiche les infos de debug si nécessaire."""
        # 1. Rendu des couches
        for layer in self.layers:
            layer.draw(screen, camera_offset)

        # 2. Rendu du Debug (Performant car la police est pré-chargée)
        if debug and self._debug_font:
            self._render_debug(screen)

    def _render_debug(self, screen: pygame.Surface) -> None:
        """Affiche les informations techniques sur le parallaxe."""
        debug_text = f"Parallax Layers: {len(self.layers)}"
        surface = self._debug_font.render(debug_text, True, (255, 255, 255))
        screen.blit(surface, (10, 10))
