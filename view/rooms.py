from __future__ import annotations

import pygame, sys

import settings
from pathlib import Path
from settings import (
    BG_COLOR,
    RED,
    ORANGE,
    YELLOW,
    FPS,
    txt,
    clamp,
    img,
    REWARD_BULLET_OFF,
    REWARD_LIFE_OFF,
    REWARD_ORB_OFF,
    REWARD_SIZE,
    PLAYER_SPAWN_OFF,
    REWARD_TEXT_XOFF,
    REWARD_TEXT_Y,
)

REWARD_FONT = 28
STATIC_DX = 30
STATIC_TEXT_DY = 40
TITLE_SIZE = 60
PROMPT_SIZE = 30
TITLE_XOFF = 170
PROMPT_XOFF = 180
PROMPT_BASE_DY = 20
from model.player import Player
from controller import debug


class Rooms:

    @staticmethod
    def reward_room(surf: pygame.Surface, pl: Player) -> None:
        clock = pygame.time.Clock()
        cx, cy = settings.SCREEN_W // 2, settings.SCREEN_H // 2
        bullet_rect = pygame.Rect(cx - REWARD_BULLET_OFF, cy - REWARD_LIFE_OFF, REWARD_SIZE, REWARD_SIZE)
        life_rect = pygame.Rect(cx - REWARD_LIFE_OFF, cy - REWARD_LIFE_OFF, REWARD_SIZE, REWARD_SIZE)
        orb_rect = pygame.Rect(cx + REWARD_ORB_OFF, cy - REWARD_LIFE_OFF, REWARD_SIZE, REWARD_SIZE)
        pl.rect.center = (settings.SCREEN_W // 2, settings.SCREEN_H - PLAYER_SPAWN_OFF)
        while True:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        pygame.quit(); sys.exit()
                    if event.key == pygame.K_h:
                        debug.toggle_hitboxes()
            keys = pygame.key.get_pressed()
            pl.update(keys, world=False)
            pl.rect.x = clamp(pl.rect.x, 0, settings.SCREEN_W - pl.rect.w)
            pl.rect.y = clamp(pl.rect.y, 0, settings.SCREEN_H - pl.rect.h)
            if pl.collision_rect().colliderect(bullet_rect):
                pl.bullet_upg += 1
                return
            if pl.collision_rect().colliderect(life_rect):
                pl.lives += 2
                return
            if pl.collision_rect().colliderect(orb_rect):
                pl.add_orbital()
                return
            surf.fill(BG_COLOR)
            if debug.SHOW_HITBOXES:
                debug.draw_hitbox(surf, pl, (0, 0))
                debug.draw_hitbox(surf, bullet_rect, (0, 0))
                debug.draw_hitbox(surf, life_rect, (0, 0))
                debug.draw_hitbox(surf, orb_rect, (0, 0))
                debug.draw_orbitals(surf, pl, (0, 0))
            else:
                pl.draw(surf, (0, 0))
                pygame.draw.rect(surf, RED, life_rect)
                pygame.draw.polygon(
                    surf,
                    YELLOW,
                    [
                        bullet_rect.midtop,
                        bullet_rect.bottomleft,
                        bullet_rect.bottomright,
                    ],
                )
                pygame.draw.circle(surf, ORANGE, orb_rect.center, REWARD_SIZE // 2)

            surf.blit(txt("TOUCH A REWARD", REWARD_FONT), (cx - REWARD_TEXT_XOFF, REWARD_TEXT_Y))
            pygame.display.flip()

    @staticmethod
    def victory_screen(surf: pygame.Surface) -> None:
        bg = img(Path("assets/UI/background/Win_screen.png"))
        Rooms._static_screen(surf, "YOU WON!", bg, dx=STATIC_DX, text_dy=STATIC_TEXT_DY)

    @staticmethod
    def game_over_screen(surf: pygame.Surface) -> None:
        Rooms._static_screen(surf, "GAME OVER")

    @staticmethod
    def _static_screen(
        surf: pygame.Surface,
        title: str,
        bg: pygame.Surface | None = None,
        dx: int = 0,
        text_dy: int = 0,
    ) -> None:
        clock = pygame.time.Clock()
        if bg is not None:
            bg = pygame.transform.scale(bg, (settings.SCREEN_W, settings.SCREEN_H))
        while True:
            clock.tick(FPS)
            surf.fill(BG_COLOR)
            if bg is not None:
                surf.blit(bg, (0, 0))
            surf.blit(
                txt(title, TITLE_SIZE),
                (settings.SCREEN_W // 2 - TITLE_XOFF + dx, settings.SCREEN_H // 2 - 60),
            )
            surf.blit(
                txt("Press ENTER to Menu", PROMPT_SIZE),
                (
                    settings.SCREEN_W // 2 - PROMPT_XOFF,
                    settings.SCREEN_H // 2 + PROMPT_BASE_DY + text_dy,
                ),
            )
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                    return
