from __future__ import annotations

import math
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

import pygame
import settings
from settings import ENEMY_BULLET_SPEED, WHITE, img

ROOT_DIR = Path(__file__).resolve().parents[1]

PROJECTILE_BASE = img(
    ROOT_DIR / "assets" / "character" / "mage" / "Projectile.png"
)
ARROW_BASE = img(
    ROOT_DIR / "assets" / "enemies" / "zombie_archer" / "arrow.png"
)

PROJECTILE_SIZE = 40
ARROW_ROT_OFFSET = 90

if TYPE_CHECKING:
    from model.player import Player


class Projectile(ABC):

    RADIUS = 20
    SCALE_SPRITE = 1.0
    SCALE_HITBOX = 1.0

    def __init__(
        self,
        x: float,
        y: float,
        dx: float,
        dy: float,
        scale_sprite: float | None = None,
        scale_hitbox: float | None = None,
    ) -> None:
        self.x, self.y, self.dx, self.dy = x, y, dx, dy
        self.scale_sprite = (
            scale_sprite if scale_sprite is not None else self.SCALE_SPRITE
        )
        self.scale_hitbox = (
            scale_hitbox if scale_hitbox is not None else self.SCALE_HITBOX
        )
        self.radius = int(self.RADIUS * self.scale_hitbox)

    def update(self) -> None:
        self.x += self.dx
        self.y += self.dy

    def off_world(self) -> bool:
        return not (
            0 <= self.x <= settings.WORLD_W and 0 <= self.y <= settings.WORLD_H
        )

    def rect(self) -> pygame.Rect:
        r = self.radius
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)

    @abstractmethod
    def draw(self, surf: pygame.Surface, cam: tuple[int, int]) -> None:
        raise NotImplementedError


class PlayerBullet(Projectile):

    def __init__(self, x: float, y: float, dx: float, dy: float, scale: float = 1.0) -> None:
        super().__init__(x, y, dx, dy, scale, scale)
        size = int(PROJECTILE_SIZE * self.scale_sprite)
        base_img = (
            PROJECTILE_BASE.convert_alpha()
            if pygame.display.get_surface()
            else PROJECTILE_BASE
        )
        self.image = pygame.transform.scale(base_img, (size, size))

    def draw(self, surf: pygame.Surface, cam: tuple[int, int]) -> None:
        surf.blit(
            self.image,
            (
                int(self.x - cam[0] - self.image.get_width() / 2),
                int(self.y - cam[1] - self.image.get_height() / 2),
            ),
        )



class EnemyBullet(Projectile):

    RADIUS = 20
    SCALE_SPRITE = 2.0

    def __init__(
        self,
        x: float,
        y: float,
        dx: float,
        dy: float,
        scale_sprite: float | None = None,
        scale_hitbox: float | None = None,
    ) -> None:
        super().__init__(x, y, dx, dy, scale_sprite, scale_hitbox)
        base_img = (
            ARROW_BASE.convert_alpha()
            if pygame.display.get_surface()
            else ARROW_BASE
        )
        w = int(base_img.get_width() * self.scale_sprite)
        h = int(base_img.get_height() * self.scale_sprite)
        scaled = pygame.transform.scale(base_img, (w, h))

        angle = -math.degrees(math.atan2(dy, dx)) - ARROW_ROT_OFFSET
        self.image = pygame.transform.rotate(scaled, angle)

    def draw(self, surf: pygame.Surface, cam: tuple[int, int]) -> None:
        surf.blit(
            self.image,
            (
                int(self.x - cam[0] - self.image.get_width() / 2),
                int(self.y - cam[1] - self.image.get_height() / 2),
            ),
        )


