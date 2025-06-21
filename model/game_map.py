from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import pygame
import settings
from .interfaces import MapProtocol
try:
    from pytmx import load_pygame, TiledMap, TiledObject
except ImportError as exc:
    raise ImportError(
        "pytmx is required to load TMX maps. Install it with 'pip install pytmx'."
    ) from exc


class GameMap(MapProtocol):

    def __init__(self, map_file: Path, scale: float = settings.MAP_SCALE) -> None:
        self.scale = scale
        self.tmx: TiledMap = load_pygame(map_file)
        self.tile_w = int(self.tmx.tilewidth * self.scale)
        self.tile_h = int(self.tmx.tileheight * self.scale)
        self.width = self.tmx.width * self.tile_w
        self.height = self.tmx.height * self.tile_h


        self.base_surface = self._render_map(
            exclude={"Doors", "Doors_nocollide", "Doors_open"}
        )
        self.closed_doors = self._render_layers(["Doors", "Doors_nocollide"])
        self.open_doors = self._render_layers(["Doors_open"])


        layers = set(self.tmx.layernames)
        if {"Walls", "Walls_back", "Decs_collide"} & layers:
            self.collides = []
            for name in ("Walls", "Walls_back", "Decs_collide"):
                if name in layers:
                    self.collides.extend(self._load_tile_collides(name))
        else:
            self.collides = self._load_objects("Collides")

        if "Doors" in layers:
            self.door_collides = self._load_tile_collides("Doors")
        else:
            self.door_collides = self._load_objects("Collides_doors")

        self.points: dict[str, Tuple[int, int]] = {}
        for layer in self.tmx.objectgroups:
            if layer.name in {
                "Player_spawn",
                "Upgrade_projectile",
                "Upgrade_health",
                "Upgrade_orbital",
            }:
                for obj in layer:
                    self.points[layer.name] = (
                        int(obj.x * self.scale),
                        int(obj.y * self.scale),
                    )
                    break

        if "Upgrade_trigger" in layers:
            self.upgrade_triggers = self._load_tile_collides("Upgrade_trigger")
        else:
            self.upgrade_triggers = []


    def _load_tile_collides(self, name: str) -> List[pygame.Rect]:
        rects: List[pygame.Rect] = []
        layer = self.tmx.get_layer_by_name(name)
        tw = int(self.tmx.tilewidth * self.scale)
        th = int(self.tmx.tileheight * self.scale)
        for x, y, gid in layer.tiles():
            if gid:
                rects.append(pygame.Rect(int(x * tw), int(y * th), tw, th))
        return rects


    def _load_objects(self, name: str) -> List[pygame.Rect]:
        rects: List[pygame.Rect] = []
        for layer in self.tmx.objectgroups:
            if layer.name != name:
                continue
            for obj in layer:
                rects.append(self._object_rect(obj))
        return rects


    def _object_rect(self, obj: TiledObject) -> pygame.Rect:
        width = obj.width or 0
        height = obj.height or 0
        x = obj.x
        y = obj.y
        if (width == 0 or height == 0) and getattr(obj, "points", None):
            xs = [pt[0] for pt in obj.points]
            ys = [pt[1] for pt in obj.points]
            x += min(xs)
            y += min(ys)
            width = max(xs) - min(xs)
            height = max(ys) - min(ys)
        rect = pygame.Rect(
            int(x * self.scale),
            int(y * self.scale),
            int(width * self.scale),
            int(height * self.scale),
        )
        return rect


    def _render_map(self, exclude: set[str] | None = None) -> pygame.Surface:
        tw, th = self.tile_w, self.tile_h
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        exclude = exclude or set()
        for layer in self.tmx.visible_layers:
            if not hasattr(layer, "tiles"):
                continue
            if layer.name in exclude:
                continue
            for x, y, gid in layer.tiles():
                tile = (
                    gid if isinstance(gid, pygame.Surface) else self.tmx.get_tile_image_by_gid(gid)
                )
                if tile:
                    tile = pygame.transform.scale(tile, (tw, th))
                    surf.blit(tile, (x * tw, y * th))
        return surf


    def _render_layers(self, names: list[str]) -> pygame.Surface:
        tw, th = self.tile_w, self.tile_h
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for name in names:
            if name not in self.tmx.layernames:
                continue
            layer = self.tmx.get_layer_by_name(name)
            if not hasattr(layer, "tiles"):
                continue
            for x, y, gid in layer.tiles():
                tile = (
                    gid if isinstance(gid, pygame.Surface) else self.tmx.get_tile_image_by_gid(gid)
                )
                if tile:
                    tile = pygame.transform.scale(tile, (tw, th))
                    surf.blit(tile, (x * tw, y * th))
        return surf


    def point(self, name: str) -> Tuple[int, int] | None:
        return self.points.get(name)


    def draw(self, surf: pygame.Surface, cam: Tuple[int, int], door_open: bool) -> None:
        surf.blit(self.base_surface, (-cam[0], -cam[1]))
        doors = self.open_doors if door_open else self.closed_doors
        surf.blit(doors, (-cam[0], -cam[1]))

