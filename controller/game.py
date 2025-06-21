from __future__ import annotations

import math
import sys
from pathlib import Path
import pygame
import audio
import music

from model.player import Player
from model.bullet import Projectile
from model.wave_manager import WaveManager
from model.game_map import GameMap
from model.enemy import Enemy
from model.effects import DeathEffect
from model.quadtree import QuadTree
import settings
from settings import FPS, ORBITAL_RADIUS, ORBITAL_HITBOX, TOTAL_WAVES, clamp
from view.camera import calc_cam

from view.renderer import Renderer
from view.rooms import Rooms
from view.pause import pause_menu
from .arena import process_arena
from .input_handler import InputHandler
from .shop import ShopController


class GameController:

    def __init__(self, surf: pygame.Surface):
        self.surf = surf
        self.map = GameMap(Path("assets/maps/arena.tmx"), settings.MAP_SCALE)
        self._set_world(self.map)
        spawn = self.map.point("Player_spawn") or (
            settings.WORLD_W // 2,
            settings.WORLD_H // 2 - settings.SPAWN_Y_OFF,
        )
        self.player = Player(spawn[0], spawn[1])
        self.pbul: list[Projectile] = []
        self.ebul: list[Projectile] = []
        self.effects: list[DeathEffect] = []
        self.shop_map = GameMap(Path("assets/maps/shop.tmx"), settings.MAP_SCALE)
        self.wave_mgr = WaveManager(self.player, self.ebul, self.map)
        self.renderer = Renderer(surf)
        self.enemy_tree = QuadTree(
            pygame.Rect(0, 0, settings.WORLD_W, settings.WORLD_H)
        )
        self.door_open = False
        self.cam = (0, 0)
        self.clock = pygame.time.Clock()
        self.running = True
        self.input = InputHandler()
        self.paused = False


    @staticmethod
    def _set_world(game_map: GameMap) -> None:
        settings.WORLD_W, settings.WORLD_H = game_map.width, game_map.height



    def loop(self) -> None:
        music.play(music.BATTLE_1_2, music.BATTLE_1_2_VOLUME)
        while self.running:
            self.clock.tick(FPS)
            self.input.poll()
            if self.input.request_exit:
                pygame.quit()
                sys.exit()
            if self.input.toggle_pause:
                self.paused = not self.paused

            if self.paused:
                if pause_menu(self.renderer, self.clock):
                    self.running = False
                    from view.menu import Menu
                    Menu(self.surf).loop()
                    return
                self.paused = False
                continue

            process_arena(self)
            self.cam = calc_cam(self.player.rect)
            self.renderer.draw_battle(self)


    def _teleport_shop(self) -> None:
        ShopController(
            self.surf,
            self.player,
            self.shop_map,
            self.wave_mgr.wave,
        ).loop()
        self._set_world(self.map)
        self.enemy_tree = QuadTree(
            pygame.Rect(0, 0, settings.WORLD_W, settings.WORLD_H)
        )
        spawn = self.map.point("Player_spawn") or (
            settings.WORLD_W // 2,
            settings.WORLD_H // 2,
        )
        self.player.rect.center = spawn
        self.pbul.clear()
        self.ebul.clear()
        self.wave_mgr.enemies.clear()
        self.wave_mgr.next_wave()
        if self.wave_mgr.wave >= 3:
            music.play(music.BATTLE_3_10, music.BATTLE_3_10_VOLUME)
        else:
            music.play(music.BATTLE_1_2, music.BATTLE_1_2_VOLUME)
        self.door_open = False


    def _bullet_collisions(self) -> None:
        for b in self.pbul[:]:
            rect = b.rect()
            for z in self.enemy_tree.query(rect):
                if z not in self.wave_mgr.enemies:
                    continue
                if z.collision_rect().collidepoint(b.x, b.y):
                    self.pbul.remove(b)
                    if isinstance(z, Enemy):
                        audio.KILL_ENEMY.play()
                        self.effects.append(
                            DeathEffect(z.x, z.y, z.death_frames())
                        )
                    self.wave_mgr.enemies.remove(z)
                    break
        for b in self.ebul[:]:
            if self.player.collision_rect().collidepoint(b.x, b.y):
                self.player.damage()
                self.ebul.remove(b)


    def _enemy_step(self, enemy: Enemy, blocks: list[pygame.Rect]) -> None:
        old_pos = (enemy.x, enemy.y)
        enemy.update(self.wave_mgr.enemies, self.cam, self.enemy_tree)
        if enemy.collider.walls(enemy, blocks):
            enemy.x, enemy.y = old_pos
        if enemy.collider.player(enemy, self.player):
            self.player.damage()
            if isinstance(enemy, Enemy):
                audio.KILL_ENEMY.play()
                self.effects.append(DeathEffect(enemy.x, enemy.y, enemy.death_frames()))
            self.wave_mgr.enemies.remove(enemy)


