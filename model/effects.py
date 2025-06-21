from __future__ import annotations

from typing import List
import pygame


class DeathEffect:

    FRAME_DELAY = 80

    def __init__(self, x: float, y: float, frames: List[pygame.Surface]):
        self.x = x
        self.y = y
        self.frames = frames
        self.index = 0
        self._last = pygame.time.get_ticks()

    def update(self) -> None:
        now = pygame.time.get_ticks()
        if now - self._last >= self.FRAME_DELAY:
            self.index += 1
            self._last = now

    def draw(self, surf: pygame.Surface, cam: tuple[int, int]) -> None:
        if self.index < len(self.frames):
            img = self.frames[self.index]
            rect = img.get_rect(center=(self.x - cam[0], self.y - cam[1]))
            surf.blit(img, rect)

    def done(self) -> bool:
        return self.index >= len(self.frames)
