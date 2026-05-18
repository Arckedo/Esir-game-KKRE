import pygame

TOPDOWN_PHASE_KEYS = {
    "top": pygame.K_z,
    "left": pygame.K_q,
    "right": pygame.K_d,
    "down": pygame.K_s,  
    "pause": pygame.K_x,
    "quit": pygame.K_p,
}

PLATFORMER_PHASE_KEYS_KEYBOARD_PLAYER = {
    "top": "JOY_0",
    #left et right sont déjà gérés par les sticks dans input_manager
    "left": pygame.K_q,
    "right": pygame.K_d,
    "down": pygame.K_s,  
    "roll": pygame.K_LSHIFT,
    "pause": pygame.K_x,
    "quit": pygame.K_p,
    "shoot" : "MOUSE_LEFT",
    "crouch": pygame.K_c,
}

PLATFORMER_PHASE_KEYS_CONTROLLER_PLAYER = {
    "top": pygame.K_UP ,
    #left et right sont déjà gérés par les sticks dans input_manager
    "top_manette" : "JOY_1",
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "down": pygame.K_DOWN,
    "roll": pygame.K_KP_0,
    "roll_manette": "JOY_0",
    "pause": pygame.K_x,
    "quit": pygame.K_p,
    "shoot" : "MOUSE_LEFT",
    "crouch": "JOY_9",
}


PLATFORMER_PHASE_KEYS_CONTROLLER_PLAYER_2 = {
    "top" : pygame.K_z,
    "top_manette" : "JOY_1",
    #left et right sont déjà gérés par les sticks dans input_manager
    "left": pygame.K_q,
    "right": pygame.K_d,
    "down": pygame.K_s,
    "roll_manette": "JOY_0",
    "roll": pygame.K_LSHIFT,
    "pause": pygame.K_x,
    "quit": pygame.K_p,
    "shoot" : "MOUSE_LEFT",
    "crouch": "JOY_9",
}
