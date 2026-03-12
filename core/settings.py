import pygame

# --- CONFIG ECRAN ---
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
LOGIC_WIDTH = 1920
LOGIC_HEIGHT = 1080
FPS = 60
TITLE = "GAMU NAMU ICI !"

# --- MAPPING DES TOUCHES (par défaut) ---
TOPDOWN_PHASE_KEYS = {
    "top": pygame.K_z,
    "left": pygame.K_q,
    "right": pygame.K_d,
    "down": pygame.K_s,
    "pause": pygame.K_x,
}
