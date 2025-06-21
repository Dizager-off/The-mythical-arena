from __future__ import annotations

import math
from pathlib import Path
from typing import List

import pygame

ROOT_DIR = Path(__file__).resolve().parents[1]

from model.bullet import PlayerBullet
import settings
import audio
from settings import (
    PLAYER_SPEED,
    PLAYER_FIRE_DELAY,
    BULLET_SPEED,
    PLAYER_SPRITE_Y_OFFSET,
    ORBITAL_RADIUS,
    ORBITAL_SIZE,
    ORBITAL_SPEED,
    clamp,
    img,
)

ORBITAL_PATH = ROOT_DIR / "assets" / "character" / "mage" / "Orbital.png"
ORBITAL_BASE = img(ORBITAL_PATH)

SPRITE_SIZE = 120
STEP_INTERVAL = 150
ATTACK_DURATION = 100
MAX_SPREAD_ANGLE = 140
SPREAD_PER_UPG = 20
STAFF_OFFSET = {
    "right": (36, 30),
    "left": (-36, 30),
    "north": (3, -54),
    "south": (-3, 57),
}
FLASH_STEP = 100


class Player(pygame.sprite.Sprite):

    def __init__(
        self,
        x: int,
        y: int,
        scale_sprite: float = 1.0,
        scale_hitbox: float = 0.75,
    ) -> None:
        super().__init__()
        self.scale_sprite = scale_sprite
        self.scale_hitbox = scale_hitbox
        self._load_images()
        base_img = ORBITAL_BASE
        if pygame.display.get_surface():
            base_img = base_img.convert_alpha()
        self.orbital_img = pygame.transform.scale(
            base_img, (ORBITAL_SIZE * 2, ORBITAL_SIZE * 2)
        )
        self.rect = self.idle["south"].get_rect(center=(x, y))
        self.lives = 3
        self.inv_until = 0
        self.flash_until = 0
        self.last_shot = 0
        self.attack_until = 0
        self.bullet_upg = 0
        self.orbital_count = 0
        self.orbital_phase = 0.0
        self.direction = "south"
        self.moving = False
        self.walk_idx = 0
        self.last_step = 0
        bbox = self.idle["south"].get_bounding_rect()
        ow = bbox.width / self.scale_sprite
        oh = bbox.height / self.scale_sprite
        self.hitbox = pygame.Rect(
            0,
            0,
            int(ow * self.scale_hitbox),
            int(oh * self.scale_hitbox),
        )


    def _load_images(self) -> None:
        root = Path(__file__).resolve().parents[1] / "assets" / "character" / "mage"

        def load(path: Path) -> pygame.Surface:
            base = img(path)
            size = int(SPRITE_SIZE * self.scale_sprite)
            return pygame.transform.scale(base, (size, size))

        self.idle: dict[str, pygame.Surface] = {
            d: load(root / "mage" / f"mage_{d}.png")
            for d in ("left", "right", "north", "south")
        }
        self.attack: dict[str, pygame.Surface] = {
            d: load(root / "mage_attack" / f"mage_attack_{d}.png")
            for d in ("left", "right", "north", "south")
        }
        self.walk: dict[str, list[pygame.Surface]] = {}
        walk_dir = root / "mage_walking_wand"
        for d in ("left", "right", "north", "south"):
            frames = [load(walk_dir / f"mage_walking_{d}_{i:04}.png") for i in range(1, 4)]
            self.walk[d] = frames

        self.staff_offset: dict[str, tuple[int, int]] = STAFF_OFFSET

    def collision_rect(self) -> pygame.Rect:
        rect = self.hitbox.copy()
        rect.center = self.rect.center
        rect.move_ip(0, 4)
        return rect


    def add_orbital(self) -> None:
        self.orbital_count += 1

    def orbital_angles(self) -> List[float]:
        if not self.orbital_count:
            return []
        step = 2 * math.pi / self.orbital_count
        return [
            (self.orbital_phase + i * step) % (2 * math.pi)
            for i in range(self.orbital_count)
        ]


    def update(self, keys: pygame.key.ScancodeWrapper, world: bool = True) -> None:
        now = pygame.time.get_ticks()
        if now >= self.attack_until:
            vx = keys[pygame.K_d] - keys[pygame.K_a]
            vy = keys[pygame.K_s] - keys[pygame.K_w]
            dist = math.hypot(vx, vy)
            if dist:
                dx = PLAYER_SPEED * vx / dist
                dy = PLAYER_SPEED * vy / dist
            else:
                dx = dy = 0
            self.moving = bool(dist)
            if self.moving:
                if abs(dx) > abs(dy):
                    self.direction = "right" if dx > 0 else "left"
                else:
                    self.direction = "south" if dy > 0 else "north"
                self.rect.x += dx
                self.rect.y += dy
                if world:
                    self.rect.x = clamp(
                        self.rect.x,
                        0,
                        settings.WORLD_W - self.rect.w,
                    )
                    self.rect.y = clamp(
                        self.rect.y,
                        0,
                        settings.WORLD_H - self.rect.h,
                    )
            else:
                self.moving = False
        else:
            self.moving = False
        if pygame.time.get_ticks() >= self.inv_until:
            self.inv_until = 0
            self.flash_until = 0
        if self.orbital_count:
            self.orbital_phase = (self.orbital_phase + ORBITAL_SPEED) % (
                2 * math.pi
            )


    def damage(self) -> None:
        if pygame.time.get_ticks() >= self.inv_until:
            self.lives = max(0, self.lives - 1)
            now = pygame.time.get_ticks()
            self.inv_until = now + settings.INVINCIBILITY
            self.flash_until = self.inv_until


    def shoot(self, dx: int, dy: int) -> list[PlayerBullet]:
        now = pygame.time.get_ticks()
        if now - self.last_shot < PLAYER_FIRE_DELAY:
            return []
        self.last_shot = now
        self.attack_until = now + ATTACK_DURATION
        audio.MAGE_ATTACK.play()
        bullets: list[PlayerBullet] = []
        ang = math.atan2(dy, dx)
        count = self.bullet_upg + 1
        spread = math.radians(min(MAX_SPREAD_ANGLE, SPREAD_PER_UPG * self.bullet_upg))
        if count == 1:
            angles = [ang]
        else:
            step = spread / (count - 1)
            start = ang - spread / 2
            angles = [start + i * step for i in range(count)]
        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "south" if dy > 0 else "north"
        for a in angles:
            vx = BULLET_SPEED * math.cos(a)
            vy = BULLET_SPEED * math.sin(a)
            off = self.staff_offset[self.direction]
            sx = self.rect.centerx + off[0]
            sy = self.rect.centery + off[1]
            bullets.append(PlayerBullet(sx, sy, vx, vy))
        return bullets


    def draw(self, surf: pygame.Surface, cam: tuple[int, int]) -> None:
        now = pygame.time.get_ticks()
        visible = True
        if now < self.flash_until:
            visible = (now // FLASH_STEP) % 2 == 0
        if visible:
            if now < self.attack_until:
                img = self.attack[self.direction]
            elif self.moving:
                if now - self.last_step > STEP_INTERVAL:
                    self.walk_idx = (self.walk_idx + 1) % len(self.walk[self.direction])
                    self.last_step = now
                img = self.walk[self.direction][self.walk_idx]
            else:
                img = self.idle[self.direction]
            surf.blit(
                img,
                self.rect.move(-cam[0], -cam[1] + PLAYER_SPRITE_Y_OFFSET),
            )

        for ang in self.orbital_angles():
            cx = self.rect.centerx + ORBITAL_RADIUS * math.cos(ang)
            cy = self.rect.centery + ORBITAL_RADIUS * math.sin(ang)
            rect = self.orbital_img.get_rect(
                center=(int(cx - cam[0]), int(cy - cam[1]))
            )
            surf.blit(self.orbital_img, rect)
