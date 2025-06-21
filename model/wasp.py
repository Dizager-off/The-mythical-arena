from __future__ import annotations

from pathlib import Path
from typing import List

import pygame

from .enemy import Enemy
from .quadtree import QuadTree
from .player import Player
from .death_animation import WaspDeathAnimation
from settings import img


class Wasp(Enemy):

    SPEED = 4
    SCALE_SPRITE = 2.0
    SCALE_HITBOX = 1.0

    def __init__(
        self,
        x: float,
        y: float,
        player: Player,
        scale_sprite: float | None = None,
        scale_hitbox: float | None = None,
    ) -> None:
        super().__init__(x, y, Wasp.SPEED, scale_sprite, scale_hitbox)
        self.player = player
        self._load_images()
        self.image = self.walk[self.direction][0]
        self.radius = int(
            self.image.get_width() / 2 * (self.scale_hitbox / self.scale_sprite)
        )


    def _load_images(self) -> None:
        root = Path(__file__).resolve().parents[1] / "assets" / "enemies" / "wasp"
        walk_dir = root / "wasp_walk"

        def load_scaled(path: Path) -> pygame.Surface:
            base = img(path)
            w = int(base.get_width() * self.scale_sprite)
            h = int(base.get_height() * self.scale_sprite)
            return pygame.transform.scale(base, (w, h))

        self.walk = {
            "left": [
                load_scaled(walk_dir / "wasp_walking_left_0001.png"),
                load_scaled(walk_dir / "wasp_walking_left_0002.png"),
            ],
            "right": [
                load_scaled(walk_dir / "wasp_walking_right_0001.png"),
                load_scaled(walk_dir / "wasp_walking_right_0002.png"),
            ],
        }
        def load_death(side: str) -> List[pygame.Surface]:
            anim = WaspDeathAnimation(side, self.scale_sprite)
            return anim.frames

        self.death = {
            "left": load_death("left"),
            "right": load_death("right"),
        }


    def death_frames(self) -> List[pygame.Surface]:
        return self.death[self.direction]


    def update(
        self,
        swarm: List[Enemy],
        cam: tuple[int, int],
        tree: "QuadTree",
    ) -> None:
        self.chase_and_collide(self.player, tree)
        self.image = self.animate_walk(self.walk)


    def draw(self, surf: pygame.Surface, cam: tuple[int, int]) -> None:
        surf.blit(self.image, self.rect().move(-cam[0], -cam[1]))
