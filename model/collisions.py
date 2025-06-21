from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING
import math
import pygame

if TYPE_CHECKING:
    from .enemy import Enemy
    from .player import Player
    from .quadtree import QuadTree


class CollisionBase(ABC):

    def walls(self, enemy: Enemy, walls: List[pygame.Rect]) -> bool:
        return any(enemy.collision_rect().colliderect(r) for r in walls)

    def player(self, enemy: Enemy, player: Player) -> bool:
        return enemy.collision_rect().colliderect(player.collision_rect())

    @abstractmethod
    def swarm(self, enemy: Enemy, tree: "QuadTree") -> None:
        raise NotImplementedError


class SameTypeCollision(CollisionBase):

    def swarm(self, enemy: Enemy, tree: "QuadTree") -> None:
        rect = enemy.collision_rect().inflate(enemy.radius * 2, enemy.radius * 2)
        for other in tree.query(rect):
            if other is enemy or type(other) is not type(enemy):
                continue
            d = math.hypot(enemy.x - other.x, enemy.y - other.y)
            other_r = getattr(
                other,
                "radius",
                getattr(other, "RADIUS", enemy.radius),
            )
            min_d = enemy.radius + other_r
            if d and d < min_d:
                push = (min_d - d) / 2
                enemy.x += (enemy.x - other.x) / d * push
                enemy.y += (enemy.y - other.y) / d * push


