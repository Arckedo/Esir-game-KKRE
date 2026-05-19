import pygame

from entities.platformer.debug import draw_text


class UITimerBar:
    """UI timer stylisé pour les joueurs."""

    def __init__(self, player, left: int, top: int, width: int = 280, height: int = 24):
        self.player = player
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    def _get_role_and_colors(self):
        is_thief = getattr(self.player, "skin_variant", None) == "player_red"

        if is_thief:
            bar_color = (60, 220, 140)
            glow_color = (80, 255, 180)
            role = "VOLEUR"
        else:
            bar_color = (235, 90, 70)
            glow_color = (255, 150, 120)
            role = "CHASSEUR"

        return role, is_thief, bar_color, glow_color

    def draw(self, screen: pygame.Surface, is_p2: bool = False):
        max_chrono = float(getattr(self.player, "max_chrono", 60.0))
        chrono = float(getattr(self.player, "chrono", max_chrono))
        ratio = 0.0 if max_chrono <= 0 else max(0.0, min(1.0, chrono / max_chrono))

        role, _, bar_color, glow_color = self._get_role_and_colors()
        center_x = self.left + self.width // 2

        try:
            box_w = 220
            box_h = 58
            box_x = center_x - box_w // 2
            box_y = self.top - box_h - 30

            bg_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            bg_surf.fill((24, 32, 64, 220))
            pygame.draw.rect(
                bg_surf, (255, 255, 255, 40), bg_surf.get_rect(), 2, border_radius=4
            )
            screen.blit(bg_surf, (box_x, box_y))

            if not pygame.font.get_init():
                pygame.font.init()
            title_font = pygame.font.SysFont("Roboto", 15)
            timer_font = pygame.font.SysFont("Roboto", 24, bold=True)

            label_player = "Player 2" if is_p2 else "Player 1"
            title_text = f"Temps {label_player}"
            timer_text = f"{chrono:0.1f}s"

            tw, _ = title_font.size(title_text)
            draw_text(screen, title_text, (center_x - tw // 2, box_y + 6), size=15)

            tw2, _ = timer_font.size(timer_text)
            draw_text(screen, timer_text, (center_x - tw2 // 2, box_y + 26), size=24)

        except Exception as e:
            print(f"Erreur rendu panneau dans UITimerBar : {e}")

        if not pygame.font.get_init():
            pygame.font.init()
        role_font = pygame.font.SysFont("Roboto", 22, bold=True)

        rw, _ = role_font.size(role)
        draw_text(
            screen,
            role,
            (center_x - rw // 2, self.top - 22),
            size=22,
            color=(255, 255, 255),
        )

        pygame.draw.rect(
            screen,
            (30, 30, 30),
            (self.left, self.top, self.width, self.height),
            border_radius=6,
        )

        fill_w = int(self.width * ratio)
        if fill_w > 0:
            pygame.draw.rect(
                screen,
                bar_color,
                (self.left, self.top, fill_w, self.height),
                border_radius=6,
            )

        pygame.draw.rect(
            screen,
            glow_color,
            (self.left, self.top, max(2, int(self.width * ratio)), self.height),
            width=2,
            border_radius=6,
        )
