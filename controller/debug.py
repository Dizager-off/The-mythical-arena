from __future__ import annotations

import math
import pygame

import settings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.player import Player

SHOW_HITBOXES = False


def toggle_hitboxes() -> None:
    global SHOW_HITBOXES
    SHOW_HITBOXES = not SHOW_HITBOXES


def draw_hitbox(
    surf: pygame.Surface,
    obj: object,
    cam: tuple[int, int],
) -> None:
    rect = None
    if hasattr(obj, "collision_rect"):
        rect = obj.collision_rect()
    elif hasattr(obj, "rect"):
        rect = obj.rect()
    elif isinstance(obj, pygame.Rect):
        rect = obj
    if rect:
        pygame.draw.rect(surf, settings.RED, rect.move(-cam[0], -cam[1]), 1)


def draw_orbitals(
    surf: pygame.Surface,
    player: "Player",
    cam: tuple[int, int],
) -> None:
    for ang in player.orbital_angles():
        cx = player.rect.centerx + settings.ORBITAL_RADIUS * math.cos(ang)
        cy = player.rect.centery + settings.ORBITAL_RADIUS * math.sin(ang)
        pygame.draw.circle(
            surf,
            settings.BLUE,
            (int(cx - cam[0]), int(cy - cam[1])),
            settings.ORBITAL_HITBOX,
            1,
        )
