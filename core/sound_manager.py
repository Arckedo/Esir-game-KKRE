import os

import pygame


class SoundManager:
    """Gestionnaire de sons avec cache et fallback silencieux."""

    _sounds: dict[str, pygame.mixer.Sound] = {}
    _enabled: bool = True
    _extensions: tuple[str, ...] = (".wav", ".mp3", ".ogg")

    @classmethod
    def setup(cls, frequency: int = 44100, size: int = -16, channels: int = 2, buffer: int = 512) -> None:
        """Initialise le mixer. Si indisponible, désactive proprement le son."""
        if pygame.mixer.get_init():
            return

        try:
            pygame.mixer.init(
                frequency=frequency,
                size=size,
                channels=channels,
                buffer=buffer,
            )
            cls._enabled = True
        except pygame.error as e:
            cls._enabled = False
            print(f"Sound disabled (mixer init failed): {e}")

    @classmethod
    def get_sound(cls, name: str) -> pygame.mixer.Sound | None:
        """Charge un son depuis assets/sounds/<name>.<ext> avec cache."""
        if not cls._enabled:
            return None

        if name not in cls._sounds:
            path = None
            for ext in cls._extensions:
                candidate = os.path.join("assets", "sounds", f"{name}{ext}")
                if os.path.exists(candidate):
                    path = candidate
                    break

            if path is None:
                return None

            try:
                cls._sounds[name] = pygame.mixer.Sound(path)
            except pygame.error as e:
                print(f"Failed to load sound '{name}': {e}")
                return None

        return cls._sounds[name]

    @classmethod
    def play(cls, name: str, volume: float = 1.0) -> None:
        """Joue le son s'il existe, sinon ne fait rien."""
        sound = cls.get_sound(name)
        if sound is None:
            return

        sound.set_volume(max(0.0, min(1.0, volume)))
        sound.play()

    # ajout de méthodes pour la musique de fond, qui utilise une API différente de pygame.mixer.music

    # méthode pour charger la musique de fond, avec support de plusieurs extensions (insirer de la méthode get_sound)
    @classmethod
    def load_music(cls, name: str) -> bool:
        """Charge une musique depuis assets/sounds/<name>.<ext>."""
        if not cls._enabled:
            print(f"Sound disabled, cannot load music '{name}'")
            return False

        path = None
        for ext in cls._extensions:
            candidate = os.path.join("assets", "sounds", f"{name}{ext}")
            if os.path.exists(candidate):
                path = candidate
                break

        if path is None:
            print(f"Music file '{name}' not found in assets/sounds/")
            return False

        try:
            pygame.mixer.music.load(path)
            print(f"Music '{name}' loaded successfully from {path}")
            return True
        except pygame.error as e:
            print(f"Failed to load music '{name}': {e}")
            return False

    # méthode pour jouer la musique de fond, avec option de boucle (inspirer de la méthode play)
    @classmethod
    def play_music(cls, name: str, volume: float = 1.0, loop: bool = False) -> None:
        """Joue la musique chargée. Si loop=True, boucle indéfiniment."""
        if not cls._enabled:
            print("Sound disabled, cannot play music")
            return

        if cls.load_music(name):
            pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
            pygame.mixer.music.play(-1 if loop else 0)
            print(f"Playing music '{name}' with loop={loop}")
        else:
            print(f"Could not load music '{name}', not playing")

    # méthode pour arrêter la musique en cours
    @classmethod
    def stop_music(cls) -> None:
        """Arrête la musique en cours."""
        if cls._enabled:
            pygame.mixer.music.stop()
