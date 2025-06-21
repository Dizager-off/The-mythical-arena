from __future__ import annotations
import pygame
import settings
from settings import clamp


def calc_cam(rect: pygame.Rect) -> tuple[int, int]:
    if settings.SCREEN_W >= settings.WORLD_W:
        cam_x = -(settings.SCREEN_W - settings.WORLD_W) // 2
    else:
        cam_x = clamp(
            rect.centerx - settings.SCREEN_W // 2,
            0,
            settings.WORLD_W - settings.SCREEN_W,
        )
    if settings.SCREEN_H >= settings.WORLD_H:
        cam_y = -(settings.SCREEN_H - settings.WORLD_H) // 2
    else:
        cam_y = clamp(
            rect.centery - settings.SCREEN_H // 2,
            0,
            settings.WORLD_H - settings.SCREEN_H,
        )
    return cam_x, cam_y
