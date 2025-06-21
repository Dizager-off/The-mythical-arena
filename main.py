import pygame

from settings import CAPTION, set_fullscreen
from view.menu import Menu


def main() -> None:
    surf = set_fullscreen()
    pygame.display.set_caption(CAPTION)
    Menu(surf).loop()


if __name__ == "__main__":
    main()
