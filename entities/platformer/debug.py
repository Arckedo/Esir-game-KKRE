import pygame


_FONT_CACHE: dict[int, pygame.font.Font] = {}


def draw_text(
    screen: pygame.Surface,
    text: str,
    pos: tuple[int, int],
    size: int = 24,
    color: tuple[int, int, int] = (255, 255, 255),
) -> None:
    """Affiche un texte à l'écran avec une petite ombre pour la lisibilité."""
    if not pygame.font.get_init():
        pygame.font.init()

    font = _FONT_CACHE.get(size)
    if font is None:
        font = pygame.font.SysFont("Roboto", size)
        _FONT_CACHE[size] = font

    shadow = font.render(text, True, (0, 0, 0))
    label = font.render(text, True, color)

    x, y = pos
    screen.blit(shadow, (x + 1, y + 1))
    screen.blit(label, (x, y))