from __future__ import annotations

from pathlib import Path
from typing import List

import pygame
from settings import img


class DeathAnimationBase:

    def __init__(self, scale: float) -> None:
        self.scale = scale
        self.frames: List[pygame.Surface] = []

    def _scale_img(self, path: Path) -> pygame.Surface:
        base = img(path)
        w = int(base.get_width() * self.scale)
        h = int(base.get_height() * self.scale)
        return pygame.transform.scale(base, (w, h))

    def _load_effect_frames(self) -> List[pygame.Surface]:
        root = (
            Path(__file__).resolve().parents[1]
            / "assets"
            / "enemies"
            / "death_effect"
        )
        frames: List[pygame.Surface] = []
        for i in range(2, 9):
            path = root / f"death_{i:04}.png"
            if path.exists():
                frames.append(self._scale_img(path))
        return frames


class SlimeDeathAnimation(DeathAnimationBase):

    def __init__(self, direction: str, scale: float) -> None:
        super().__init__(scale)
        root = (
            Path(__file__).resolve().parents[1]
            / "assets"
            / "enemies"
            / "slime"
            / "slime_death"
        )
        first = root / f"slime_death_{direction}_0001.png"
        self.frames = [self._scale_img(first)] + self._load_effect_frames()


class WaspDeathAnimation(DeathAnimationBase):

    def __init__(self, direction: str, scale: float) -> None:
        super().__init__(scale)
        root = (
            Path(__file__).resolve().parents[1]
            / "assets"
            / "enemies"
            / "wasp"
            / "wasp_death"
        )
        first = root / f"wasp_death_{direction}_0001.png"
        self.frames = [self._scale_img(first)] + self._load_effect_frames()

class ZombieArcherDeathAnimation(DeathAnimationBase):

    def __init__(self, direction: str, scale: float) -> None:
        super().__init__(scale)
        root = (
            Path(__file__).resolve().parents[1]
            / "assets"
            / "enemies"
            / "zombie_archer"
            / "zombie_archer_death"
        )
        first = root / f"zombie_archer_death_{direction}_0001.png"
        self.frames = [self._scale_img(first)] + self._load_effect_frames()

