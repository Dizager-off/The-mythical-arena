from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List
import math
import pygame

from .collisions import CollisionBase, SameTypeCollision
from .quadtree import QuadTree


class Enemy(ABC):

    SPEED = 1.0
    RADIUS = 20
    SCALE_SPRITE = 1.0
    SCALE_HITBOX = 1.0

    def __init__(
        self,
        x: float,
        y: float,
        speed: float | None = None,
        scale_sprite: float | None = None,
        scale_hitbox: float | None = None,
        collider: CollisionBase | None = None,
    ) -> None:
        self.x, self.y = x, y
        self.speed = speed if speed is not None else self.SPEED
        self.scale_sprite = scale_sprite if scale_sprite is not None else self.SCALE_SPRITE
        self.scale_hitbox = (
            scale_hitbox if scale_hitbox is not None else self.SCALE_HITBOX
        )
        self.radius = int(self.RADIUS * self.scale_hitbox)
        self.collider = collider or SameTypeCollision()
        self.direction = "right"
        self.walk_idx = 0
        self.last_step = 0

    def rect(self) -> pygame.Rect:
        img = getattr(self, "image", None)
        if img is not None:
            return pygame.Rect(
                self.x - img.get_width() // 2,
                self.y - img.get_height() // 2,
                img.get_width(),
                img.get_height(),
            )
        r = self.radius
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)

    def collision_rect(self) -> pygame.Rect:
        img = getattr(self, "image", None)
        if img is not None:
            ow = img.get_width() / self.scale_sprite
            oh = img.get_height() / self.scale_sprite
            w = int(ow * self.scale_hitbox)
            h = int(oh * self.scale_hitbox)
            return pygame.Rect(self.x - w // 2, self.y - h // 2, w, h)
        return self.rect()

    @abstractmethod
    def update(
        self,
        swarm: List["Enemy"],
        cam: tuple[int, int],
        tree: "QuadTree",
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw(self, surf: pygame.Surface, cam: tuple[int, int]) -> None:
        raise NotImplementedError

    def death_frames(self) -> List[pygame.Surface]:
        return []


    def chase_player(self, player: "Player") -> tuple[float, float, float]:
        dx = player.rect.centerx - self.x
        dy = player.rect.centery - self.y
        dist = math.hypot(dx, dy) or 1
        self.direction = "right" if dx > 0 else "left"
        self.x += self.speed * dx / dist
        self.y += self.speed * dy / dist
        return dist, dx, dy

    def animate_walk(
        self, frames: dict[str, list[pygame.Surface]], step_ms: int = 200
    ) -> pygame.Surface:
        now = pygame.time.get_ticks()
        if now - self.last_step > step_ms:
            self.walk_idx = (self.walk_idx + 1) % len(frames[self.direction])
            self.last_step = now
        return frames[self.direction][self.walk_idx]

    def chase_and_collide(
        self, player: "Player", tree: "QuadTree"
    ) -> tuple[float, float, float]:
        dist, dx, dy = self.chase_player(player)
        self.collider.swarm(self, tree)
        return dist, dx, dy

