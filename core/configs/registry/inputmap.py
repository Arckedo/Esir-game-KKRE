import pygame

TOPDOWN_PHASE_KEYS = {
    "top": pygame.K_z,
    "left": pygame.K_q,
    "right": pygame.K_d,
    "down": pygame.K_s,  
    "pause": pygame.K_x,
    "quit": pygame.K_p,
}

PLATFORMER_PHASE_KEYS_PLAYER1 = {
    "top": pygame.K_z,
    "left": pygame.K_q,
    "right": pygame.K_d,
    "down": pygame.K_s,  
    "roll": pygame.K_LSHIFT,
    "pause": pygame.K_x,
    "quit": pygame.K_p,
    "shoot" : "MOUSE_LEFT",
}

PLATFORMER_PHASE_KEYS_PLAYER2 = {
    "top": pygame.K_UP,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "down": pygame.K_DOWN,
    "roll": pygame.K_RSHIFT,
    "pause": pygame.K_x,
    "quit": pygame.K_p,
    "shoot" : "MOUSE_LEFT",
}