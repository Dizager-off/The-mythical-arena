from __future__ import annotations

import sys
from pathlib import Path
import pygame
import audio
import music

import settings
from settings import FPS, BG_COLOR, clamp, img
from view.camera import calc_cam
from view.renderer import _draw_hud, HEART_PATH
from .input_handler import InputHandler
from model.player import Player
from model.game_map import GameMap
from controller import debug


class ShopController:

    def __init__(
        self, surf: pygame.Surface, player: Player, game_map: GameMap, wave: int
    ) -> None:
        self.surf = surf
        self.player = player
        self.map = game_map
        self.input = InputHandler()
        self.clock = pygame.time.Clock()
        self.running = True
        self.wave = wave
        self.cam = (0, 0)
        self.reward_taken = False
        settings.WORLD_W, settings.WORLD_H = self.map.width, self.map.height
        triggers = sorted(self.map.upgrade_triggers, key=lambda r: r.x)
        if len(triggers) >= 3:
            self.bullet_rect, self.life_rect, self.orb_rect = triggers[:3]
        else:
            self.bullet_rect = self.life_rect = self.orb_rect = pygame.Rect(0, 0, 0, 0)
        self.bullet_pos = self.map.point("Upgrade_projectile") or self.bullet_rect.center
        self.life_pos = self.map.point("Upgrade_health") or self.life_rect.center
        self.orb_pos = self.map.point("Upgrade_orbital") or self.orb_rect.center
        self.bullet_img = img(Path("assets/character/mage/Projectile.png"))
        life_base = img(Path("assets/character/mage/Heart_upgrade.png"))
        self.life_img = pygame.transform.scale(
            life_base,
            (
                int(life_base.get_width() * settings.HEART_SCALE),
                int(life_base.get_height() * settings.HEART_SCALE),
            ),
        )
        self.orb_img = img(Path("assets/character/mage/Orbital.png"))
        heart_base = img(HEART_PATH)
        size = (
            int(heart_base.get_width() * settings.HEART_SCALE),
            int(heart_base.get_height() * settings.HEART_SCALE),
        )
        self.heart_img = pygame.transform.scale(heart_base, size)
        spawn = self.map.point("Player_spawn") or (
            settings.WORLD_W // 2,
            settings.WORLD_H - settings.SPAWN_HAZE,
        )
        self.player.rect.center = spawn



    def loop(self) -> None:
        music.play(music.SHOP, music.SHOP_VOLUME)
        while self.running:
            self.clock.tick(FPS)
            self.input.poll()
            if self.input.request_exit:
                pygame.quit(); sys.exit()
            if self.input.teleport:
                break
            keys = self.input.keys or pygame.key.get_pressed()
            old_pos = self.player.rect.topleft
            self.player.update(keys)
            if any(self.player.collision_rect().colliderect(r) for r in self.map.collides):
                self.player.rect.topleft = old_pos
            if not self.reward_taken:
                if self.player.collision_rect().colliderect(self.bullet_rect):
                    self.player.bullet_upg += 1
                    audio.PICKUP.play()
                    self.reward_taken = True
                elif self.player.collision_rect().colliderect(self.life_rect):
                    self.player.lives += 2
                    audio.PICKUP.play()
                    self.reward_taken = True
                elif self.player.collision_rect().colliderect(self.orb_rect):
                    self.player.add_orbital()
                    audio.PICKUP.play()
                    self.reward_taken = True
            if (
                self.reward_taken
                and self.player.rect.bottom >= settings.WORLD_H
            ):
                break
            self.cam = calc_cam(self.player.rect)
            self._draw()


    def _draw(self) -> None:
        cam = self.cam
        self.surf.fill(BG_COLOR)
        self.map.draw(self.surf, cam, True)

        if debug.SHOW_HITBOXES:
            debug.draw_hitbox(self.surf, self.player, cam)
            debug.draw_orbitals(self.surf, self.player, cam)
            if not self.reward_taken:
                debug.draw_hitbox(self.surf, self.bullet_rect, cam)
                debug.draw_hitbox(self.surf, self.life_rect, cam)
                debug.draw_hitbox(self.surf, self.orb_rect, cam)
            for r in self.map.collides:
                debug.draw_hitbox(self.surf, r, cam)
        else:
            self.player.draw(self.surf, cam)
            if not self.reward_taken:
                self.surf.blit(
                    self.bullet_img,
                    self.bullet_img.get_rect(
                        center=(self.bullet_pos[0] - cam[0], self.bullet_pos[1] - cam[1])
                    ),
                )
                self.surf.blit(
                    self.life_img,
                    self.life_img.get_rect(
                        center=(self.life_pos[0] - cam[0], self.life_pos[1] - cam[1])
                    ),
                )
                self.surf.blit(
                    self.orb_img,
                    self.orb_img.get_rect(
                        center=(self.orb_pos[0] - cam[0], self.orb_pos[1] - cam[1])
                    ),
                )
        _draw_hud(self.surf, self.wave, self.player.lives, self.heart_img)
        pygame.display.flip()
