
from __future__ import annotations

import pygame

from settings import PLAYER_FIRE_DELAY
from . import debug

class InputHandler:

    _DIR_KEYS = {
        pygame.K_a: (-1, 0),
        pygame.K_d: (1, 0),
        pygame.K_w: (0, -1),
        pygame.K_s: (0, 1),
    }
    _ARROW_KEYS = {
        pygame.K_LEFT: (-1, 0),
        pygame.K_RIGHT: (1, 0),
        pygame.K_UP: (0, -1),
        pygame.K_DOWN: (0, 1),
    }

    def __init__(self):
        self._keys = None
        self.teleport = False
        self.request_exit = False
        self.toggle_pause = False
        self.shoot_dirs: list[tuple[int, int]] = []
        self._last_shot = 0

    def poll(self) -> None:
        self.teleport = False
        self.request_exit = False
        self.toggle_pause = False
        self.shoot_dirs.clear()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.request_exit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.request_exit = True
                elif event.key == pygame.K_ESCAPE:
                    self.toggle_pause = True
                elif event.key == pygame.K_f:
                    self.teleport = True
                elif event.key == pygame.K_h:
                    debug.toggle_hitboxes()
        self._keys = pygame.key.get_pressed()

        now = pygame.time.get_ticks()
        if self._keys and now - self._last_shot >= PLAYER_FIRE_DELAY:
            for key, vec in self._ARROW_KEYS.items():
                if self._keys[key]:
                    self.shoot_dirs.append(vec)
            if self.shoot_dirs:
                self._last_shot = now
                self.shoot_dirs = self.shoot_dirs[:1]

    @property
    def movement(self) -> tuple[int, int]:
        if not self._keys:
            return 0, 0
        dx = dy = 0
        for key, (vx, vy) in self._DIR_KEYS.items():
            if self._keys[key]:
                dx += vx
                dy += vy
        return dx, dy

    @property
    def keys(self) -> pygame.key.ScancodeWrapper | None:
        return self._keys
