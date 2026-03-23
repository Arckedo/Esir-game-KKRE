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
    "top": "JOY_0",
    #left et right sont déjà gérés par les sticks dans input_manager
    "left": pygame.K_q,
    "right": pygame.K_d,
    "down": pygame.K_s,  
    "roll": "JOY_1",
    "pause": pygame.K_x,
    "quit": pygame.K_p,
    "shoot" : "MOUSE_LEFT",
    "crouch": "JOY_9",
}

PLATFORMER_PHASE_KEYS_PLAYER2 = {
    "top": "JOY_1",
    #left et right sont déjà gérés par les sticks dans input_manager
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "down": pygame.K_DOWN,
    "roll": "JOY_0",
    "pause": pygame.K_x,
    "quit": pygame.K_p,
    "shoot" : "MOUSE_LEFT",
    "crouch": "JOY_9",
}