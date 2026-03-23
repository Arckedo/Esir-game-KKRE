import ctypes
import os
import platform

import pygame

import core.configs.settings as stgs
from core.sound_manager import SoundManager
from core.state_manager import StateManager
from states.phase.platformer import PlatformerPhase

# --- DPI Awareness (Windows) ---
if platform.system() == "Windows":
    try:
        # On dit à Windows de NE PAS toucher à la mise à l'échelle
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()


class Game:
    """Classe orchestrant la boucle de jeu"""

    def __init__(self) -> None:
        pygame.init()
        SoundManager.setup()
        pygame.joystick.init()  # Initialisation des manettes
        self.joysticks = []
        self.player1_joystick = None
        self.player2_joystick = None

        # Récupère les manettes déjà branchées au lancement.
        for device_index in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(device_index)
            joystick.init()
            self.joysticks.append(joystick)
        self._update_player_joystick_slots()

        # Dimension interne du jeu
        self.w, self.h = stgs.SCREEN_WIDTH, stgs.SCREEN_HEIGHT

        # Configuration de l'écran pour le rendu.
        self.screen = pygame.display.set_mode(
            (self.w, self.h), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
        )

        # Sert à conserver les bords nets des Pixels Arts lors d'un redimensionnement
        os.environ["SDL_RENDER_SCALE_QUALITY"] = "0"

        # Initialisation du StateManager (Gestionnaire d'Etats, de scènes)
        # On lance la première scène du jeu directement (push).
        self.manager = StateManager()
        self.manager.push(PlatformerPhase())

        # Variables de temps pour la boucle de jeu
        self.clock = pygame.time.Clock()  # Horloge limitant les FPS
        self.dt = 0.0  # Delta time (utile pour la physique)
        self.running = True  # Permet de laisser ouverte l'application

        # Monitoring : Statistiques et performance
        self.min_fps = 60.0
        self.frame_count = 0

    def run(self) -> None:
        """Boucle de jeu principale"""
        while self.running:
            # ---------- CHRONOMETRIE -----------
            self.dt = self.clock.tick(60) / 1000.0
            self.current_fps = self.clock.get_fps()

            # ---------- SURVEILLLAGE PERFORMANCE -----------
            # On ignore les premières frames pour laisser au pc le temps de se stabiliser
            self.frame_count += 1
            if self.frame_count > 60:
                if 0 < self.current_fps < self.min_fps:
                    self.min_fps = self.current_fps

            # Affiche les FPS dans la console, toutes les secondes.
            if self.frame_count % 60 == 0:
                print(f"FPS: {int(self.current_fps)} | Min: {int(self.min_fps)}")

            # ---------- GESTION DES ÉVÉNEMENTS GLOBAUX -----------
            events = pygame.event.get()
            # Permet de quitter le jeu peut importe l'état/scène et ajout de la gestion de manettes (connecter/déconnecter)
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.JOYDEVICEADDED:
                    joystick = pygame.joystick.Joystick(event.device_index)
                    joystick.init()
                    self.joysticks.append(joystick)
                    self._update_player_joystick_slots()
                    print(f"Manette connectee: {joystick.get_name()}")
                elif event.type == pygame.JOYDEVICEREMOVED:
                    self.joysticks = [
                        joy
                        for joy in self.joysticks
                        if joy.get_instance_id() != event.instance_id
                    ]
                    self._update_player_joystick_slots()
                    print(f"Manette deconnectee: id={event.instance_id}")

            # ---------- LOGIQUE DES STATES ----------
            # On récupère l'état actif et on lui délègue la logique et le rendu<
            current_state = self.manager.current()
            current_state.handle_events(events, self)
            current_state.update(self)

            # ---------- RENDU VISUEL ----------

            # On nettoie l'écran
            self.screen.fill((0, 0, 0))

            # On dessine la scène/ l'état
            current_state.draw(self.screen, self.current_fps)

            # Envoie l'image à pygame pour l'afficher
            pygame.display.flip()

        # Ferme proprement Pygame
        pygame.quit()

    def _update_player_joystick_slots(self) -> None:
        """Affecte la 1ere manette au joueur 1 et la 2eme au joueur 2."""
        if len(self.joysticks) >= 1:
            self.player1_joystick = self.joysticks[0]  
        else :
            self.player1_joystick = None
        if len(self.joysticks) >= 2:
            self.player2_joystick = self.joysticks[1]
        else:
            self.player2_joystick = None


if __name__ == "__main__":
    Game().run()
