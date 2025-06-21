from __future__ import annotations

from typing import List, Protocol, Tuple

import pygame


class MapProtocol(Protocol):

    collides: List[pygame.Rect]
    door_collides: List[pygame.Rect]

    def draw(self, surf: pygame.Surface, cam: Tuple[int, int], door_open: bool) -> None:
        ...

