from __future__ import annotations

import math
import random
from typing import List, TYPE_CHECKING
import pygame

from model.enemy import Enemy
from model.zombie_archer import ZombieArcher
from model.slime import Slime
from model.wasp import Wasp
from model.bullet import Projectile
from model.interfaces import MapProtocol
import settings
from settings import SPAWN_MIN_DIST, SPAWN_RANGE, TICKET, TOTAL_WAVES, clamp

if TYPE_CHECKING:
    from model.player import Player


class WaveManager:

    def __init__(
        self,
        player: Player,
        enemy_bullets: list[Projectile],
        game_map: MapProtocol,
    ) -> None:
        self.player = player
        self.enemy_bullets = enemy_bullets
        self.map = game_map
        self.wave = 1
        self.enemies: List[Enemy] = []
        self._pending: List[str] = self._plan_wave()
        self._next_spawn = 0

    def cleared(self) -> bool:
        return not self.enemies and not self._pending

    def next_wave(self) -> None:
        if self.wave < TOTAL_WAVES:
            self.wave += 1
            self.enemies.clear()
            self._pending = self._plan_wave()
            self._next_spawn = 0


    def update(self) -> None:
        now = pygame.time.get_ticks()
        if self._pending and now >= self._next_spawn:
            for _ in range(settings.WAVE_SPAWN_BATCH):
                if not self._pending:
                    break
                kind = self._pending.pop(0)
                self.enemies.append(self._spawn(kind))
            self._next_spawn = now + settings.WAVE_SPAWN_DELAY


    def _spawn(self, kind: str) -> Enemy:
        blocks = self.map.collides + self.map.door_collides
        for _ in range(settings.SPAWN_TRIES):
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(SPAWN_MIN_DIST, SPAWN_MIN_DIST + SPAWN_RANGE)
            x = clamp(
                self.player.rect.centerx + math.cos(ang) * dist,
                0,
                settings.WORLD_W,
            )
            y = clamp(
                self.player.rect.centery + math.sin(ang) * dist,
                0,
                settings.WORLD_H,
            )
            if self.player.collision_rect().collidepoint(x, y):
                continue
            enemy = self._create_enemy(kind, x, y)
            rect = enemy.collision_rect()
            if any(rect.colliderect(b) for b in blocks):
                continue
            return enemy
        x = clamp(self.player.rect.centerx + SPAWN_MIN_DIST, 0, settings.WORLD_W)
        y = clamp(self.player.rect.centery, 0, settings.WORLD_H)
        return self._create_enemy(kind, x, y)

    def _create_enemy(self, kind: str, x: float, y: float) -> Enemy:
        if kind == "slime":
            return Slime(x, y, self.player)
        if kind == "wasp":
            return Wasp(x, y, self.player)
        if kind == "zombie_archer":
            return ZombieArcher(x, y, self.player, self.enemy_bullets)
        raise ValueError(f"Unknown enemy kind: {kind}")

    def _plan_wave(self) -> List[str]:
        budget = int(settings.WAVE_BUDGET_BASE * (settings.WAVE_BUDGET_GROWTH ** (self.wave - 1)))
        allowed = (
            ["slime"]
            if self.wave == 1
            else ["slime", "wasp"]
            if self.wave == 2
            else ["slime", "wasp", "zombie_archer"]
        )
        swarm: List[str] = []
        archers = 0
        while True:
            avail = allowed[:]
            if archers >= settings.ARCHER_CAP and "zombie_archer" in avail:
                avail.remove("zombie_archer")
            if not avail:
                break
            min_ticket = min(TICKET[k] for k in avail)
            if budget < min_ticket:
                break
            kind = random.choice(avail)
            if TICKET[kind] <= budget:
                budget -= TICKET[kind]
                if kind == "zombie_archer":
                    archers += 1
                swarm.append(kind)
        random.shuffle(swarm)
        return swarm
