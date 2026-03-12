import pygame

TOPDOWN_PHASE_KEYS = {
    "top": pygame.K_z,
    "left": pygame.K_q,
    "right": pygame.K_d,
    "down": pygame.K_s,  
    "pause": pygame.K_x,
    "quit": pygame.K_p,
}

PLATFORMER_PHASE_KEYS = {
    "top": pygame.K_z,
    "left": pygame.K_q,
    "right": pygame.K_d,
    "down": pygame.K_s,  
    "pause": pygame.K_x,
    "quit": pygame.K_p,
    "shoot" : "MOUSE_LEFT",
}