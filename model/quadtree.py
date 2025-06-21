from __future__ import annotations

from typing import Any, List, Tuple
import pygame


class QuadTree:

    def __init__(
        self,
        bounds: pygame.Rect,
        capacity: int = 4,
        max_depth: int = 5,
        depth: int = 0,
    ) -> None:
        self.bounds = bounds
        self.capacity = capacity
        self.max_depth = max_depth
        self.depth = depth
        self.objects: List[Tuple[Any, pygame.Rect]] = []
        self.nodes: List["QuadTree"] = []

    def clear(self) -> None:
        self.objects.clear()
        for n in self.nodes:
            n.clear()
        self.nodes.clear()

    def _split(self) -> None:
        if self.nodes:
            return
        w, h = self.bounds.width // 2, self.bounds.height // 2
        x, y = self.bounds.topleft
        self.nodes = [
            QuadTree(pygame.Rect(x, y, w, h), self.capacity, self.max_depth, self.depth + 1),
            QuadTree(
                pygame.Rect(x + w, y, w, h),
                self.capacity,
                self.max_depth,
                self.depth + 1,
            ),
            QuadTree(
                pygame.Rect(x, y + h, w, h),
                self.capacity,
                self.max_depth,
                self.depth + 1,
            ),
            QuadTree(
                pygame.Rect(x + w, y + h, w, h),
                self.capacity,
                self.max_depth,
                self.depth + 1,
            ),
        ]

    def _index(self, rect: pygame.Rect) -> int:
        mid_x = self.bounds.centerx
        mid_y = self.bounds.centery
        top = rect.bottom < mid_y
        bottom = rect.top > mid_y
        left = rect.right < mid_x
        right = rect.left > mid_x
        if top:
            if left:
                return 0
            if right:
                return 1
        if bottom:
            if left:
                return 2
            if right:
                return 3
        return -1

    def insert(self, obj: Any, rect: pygame.Rect) -> None:
        if self.nodes:
            idx = self._index(rect)
            if idx != -1:
                self.nodes[idx].insert(obj, rect)
                return
        self.objects.append((obj, rect))
        if (
            len(self.objects) > self.capacity
            and self.depth < self.max_depth
            and not self.nodes
        ):
            self._split()
            for o, r in self.objects[:]:
                idx = self._index(r)
                if idx != -1:
                    self.nodes[idx].insert(o, r)
                    self.objects.remove((o, r))

    def query(self, rect: pygame.Rect, found: List[Any] | None = None) -> List[Any]:
        if found is None:
            found = []
        if self.nodes:
            idx = self._index(rect)
            if idx != -1:
                self.nodes[idx].query(rect, found)
            else:
                for n in self.nodes:
                    if n.bounds.colliderect(rect):
                        n.query(rect, found)
        for o, r in self.objects:
            if r.colliderect(rect):
                found.append(o)
        return found
