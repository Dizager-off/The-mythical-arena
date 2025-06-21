from __future__ import annotations

import math
from pathlib import Path
from typing import List

import pygame

from .enemy import Enemy
from .player import Player
from .bullet import EnemyBullet
from .death_animation import ZombieArcherDeathAnimation
from .collisions import SameTypeCollision
from .quadtree import QuadTree
import settings
import audio
from settings import ENEMY_BULLET_SPEED, img

HITBOX_W_OFF = 80
HITBOX_H_OFF = 20
ANIM_STEP = 200
SHOOT_DELAY = 2_000
BOW_OFFSET = 20


class ZombieArcher(Enemy):

    SPEED = 2
    SCALE_SPRITE = 2.4
    SCALE_HITBOX = 1.0

    def __init__(
        self,
        x: float,
        y: float,
        player: Player,
        enemy_bullets: List[EnemyBullet],
        scale_sprite: float | None = None,
        scale_hitbox: float | None = None,
    ) -> None:
        super().__init__(x, y, ZombieArcher.SPEED, scale_sprite, scale_hitbox, SameTypeCollision())
        self.player = player
        self.enemy_bullets = enemy_bullets
        self.last_shot = 0
        self._load_images()
        self.body_img = self.walk_body[self.direction][0]
        self.head_img = self.walk_head[self.direction][0]
        w = int(self.body_img.get_width() * self.scale_hitbox) - HITBOX_W_OFF
        self.radius = max(1, w // 2)


    def _load_images(self) -> None:
        root = Path(__file__).resolve().parents[1] / "assets" / "enemies" / "zombie_archer"
        walk_root = root / "zombie_archer_walk"

        def load_scaled(path: Path) -> pygame.Surface:
            base = img(path)
            w = int(base.get_width() * self.scale_sprite)
            h = int(base.get_height() * self.scale_sprite)
            return pygame.transform.scale(base, (w, h))

        body_dir = walk_root / "body"
        head_dir = walk_root / "head"
        self.walk_body = {
            "left": [
                load_scaled(body_dir / "zombie_archer_walking_body_left_0001.png"),
                load_scaled(body_dir / "zombie_archer_walking_body_left_0002.png"),
            ],
            "right": [
                load_scaled(body_dir / "zombie_archer_walking_body_right_0001.png"),
                load_scaled(body_dir / "zombie_archer_walking_body_right_0002.png"),
            ],
        }
        self.walk_head = {
            "left": [
                load_scaled(head_dir / "zombie_archer_walking_head_left_0001.png"),
                load_scaled(head_dir / "zombie_archer_walking_head_left_0002.png"),
            ],
            "right": [
                load_scaled(head_dir / "zombie_archer_walking_head_right_0001.png"),
                load_scaled(head_dir / "zombie_archer_walking_head_right_0002.png"),
            ],
        }
        self.bow_base = load_scaled(root / "bow.png")
        self.bow_frames = {
            ang: pygame.transform.rotate(self.bow_base, ang)
            for ang in range(0, 360, settings.BOW_ANGLE_STEP)
        }

        def load_death(side: str) -> List[pygame.Surface]:
            anim = ZombieArcherDeathAnimation(side, self.scale_sprite)
            return anim.frames

        self.death = {"left": load_death("left"), "right": load_death("right")}


    def death_frames(self) -> List[pygame.Surface]:
        return self.death[self.direction]


    def rect(self) -> pygame.Rect:
        img = self.body_img
        return pygame.Rect(
            self.x - img.get_width() // 2,
            self.y - img.get_height() // 2,
            img.get_width(),
            img.get_height(),
        )

    def collision_rect(self) -> pygame.Rect:
        img = self.body_img
        w = int(img.get_width() * self.scale_hitbox) - HITBOX_W_OFF
        h = int(img.get_height() * self.scale_hitbox) - HITBOX_H_OFF
        w = max(1, w)
        h = max(1, h)
        return pygame.Rect(self.x - w // 2, self.y - h // 2, w, h)


    def update(
        self,
        swarm: List[Enemy],
        cam: tuple[int, int],
        tree: "QuadTree",
    ) -> None:
        dist, dx, dy = self.chase_and_collide(self.player, tree)
        now = pygame.time.get_ticks()
        self.body_img = self.animate_walk(self.walk_body, ANIM_STEP)
        self.head_img = self.animate_walk(self.walk_head, ANIM_STEP)
        if (
            0 <= self.x - cam[0] <= settings.SCREEN_W
            and 0 <= self.y - cam[1] <= settings.SCREEN_H
        ):
            if now - self.last_shot >= SHOOT_DELAY:
                self.last_shot = now
                vx = ENEMY_BULLET_SPEED * dx / dist
                vy = ENEMY_BULLET_SPEED * dy / dist
                audio.BOW.play()
                self.enemy_bullets.append(EnemyBullet(self.x, self.y, vx, vy))


    def draw(self, surf: pygame.Surface, cam: tuple[int, int]) -> None:
        body_rect = self.rect().move(-cam[0], -cam[1])
        surf.blit(self.body_img, body_rect)
        ang = math.atan2(
            self.player.rect.centery - self.y,
            self.player.rect.centerx - self.x,
        )
        bow_angle = -math.degrees(ang)
        step = (
            int(round(bow_angle / settings.BOW_ANGLE_STEP))
            * settings.BOW_ANGLE_STEP
        ) % 360
        bow_img = self.bow_frames[step]
        off_x = math.cos(ang) * BOW_OFFSET
        off_y = math.sin(ang) * BOW_OFFSET
        bow_rect = bow_img.get_rect(
            center=(body_rect.centerx + off_x, body_rect.centery + off_y)
        )
        surf.blit(bow_img, bow_rect)
        surf.blit(self.head_img, body_rect)

