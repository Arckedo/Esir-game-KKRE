import pygame

WIDTH, HEIGHT = 900, 600
BG = (20, 20, 30)
FG = (230, 230, 230)
GREEN = (80, 220, 120)
RED = (230, 80, 80)

def main():
    """Test de détection et d'affichage des manettes avec Pygame. Affiche les boutons, axes et hats actifs."""
    pygame.init()
    pygame.joystick.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Test joystick pygame")
    font = pygame.font.SysFont("consolas", 22)
    clock = pygame.time.Clock()

    joysticks = {}

    # Charge les manettes déjà branchées
    for i in range(pygame.joystick.get_count()):
        js = pygame.joystick.Joystick(i)
        js.init()
        joysticks[js.get_instance_id()] = js

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.JOYDEVICEADDED:
                js = pygame.joystick.Joystick(event.device_index)
                js.init()
                joysticks[js.get_instance_id()] = js

            elif event.type == pygame.JOYDEVICEREMOVED:
                if event.instance_id in joysticks:
                    del joysticks[event.instance_id]

        screen.fill(BG)

        if not joysticks:
            txt = font.render("Aucune manette detectee", True, RED)
            screen.blit(txt, (20, 20))
        else:
            y = 20
            for instance_id, js in joysticks.items():
                header = f"Manette id={instance_id} | {js.get_name()}"
                screen.blit(font.render(header, True, GREEN), (20, y))
                y += 35

                # Boutons
                pressed_buttons = []
                for b in range(js.get_numbuttons()):
                    if js.get_button(b):
                        pressed_buttons.append(str(b))
                b_txt = "Boutons presses: " + (", ".join(pressed_buttons) if pressed_buttons else "aucun")
                screen.blit(font.render(b_txt, True, FG), (40, y))
                y += 30

                # Axes (sticks/triggers)
                axes_values = []
                for a in range(js.get_numaxes()):
                    v = js.get_axis(a)
                    axes_values.append(f"A{a}:{v:+.2f}")
                a_txt = "Axes: " + " | ".join(axes_values)
                screen.blit(font.render(a_txt, True, FG), (40, y))
                y += 30

                # Hats (croix directionnelle)
                hats_values = []
                for h in range(js.get_numhats()):
                    hv = js.get_hat(h)  # tuple (x, y)
                    hats_values.append(f"H{h}:{hv}")
                h_txt = "Hats: " + (" | ".join(hats_values) if hats_values else "aucun")
                screen.blit(font.render(h_txt, True, FG), (40, y))
                y += 45

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()