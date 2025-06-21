from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
import pygame

import settings
from settings import (
    BG_COLOR,
    txt,
    TOTAL_WAVES,
    img,
    BTN_W,
    BTN_H,
    BTN_SPACING,
    PAUSE_TEXT_OFF,
)

HUD_FONT = 28
HUD_WAVE_POS = (20, 20)
HUD_HEART_POS = (20, 60)
HUD_LIVES_DX = 10
HUD_LIVES_Y = 70
PAUSE_TITLE_SIZE = 60
PAUSE_BTN_SIZE = 38

HEART_PATH = (
    Path(__file__).resolve().parents[1] / "assets" / "UI" / "heart.png"
)
BTN_PATH = Path("assets/UI/button")
PAUSE_BG_PATH = Path("assets/UI/background/Pause_screen.png")

from controller import debug

if TYPE_CHECKING:
    from controller.game import GameController


def _draw_hud(
    surf: pygame.Surface, wave: int, lives: int, heart_img: pygame.Surface
) -> None:
    surf.blit(txt(f"Wave: {wave}/{TOTAL_WAVES}", HUD_FONT), HUD_WAVE_POS)
    surf.blit(heart_img, HUD_HEART_POS)
    surf.blit(
        txt(f"x{lives}", HUD_FONT),
        (HUD_HEART_POS[0] + heart_img.get_width() + HUD_LIVES_DX, HUD_LIVES_Y),
    )


class Renderer:

    def __init__(self, surf: pygame.Surface):
        self.surf = surf
        base = img(HEART_PATH)
        size = (
            int(base.get_width() * settings.HEART_SCALE),
            int(base.get_height() * settings.HEART_SCALE),
        )
        self.heart = pygame.transform.scale(base, size)
        base = img(BTN_PATH / "button.png")
        hover = img(BTN_PATH / "button_hover.png")
        size = (settings.BTN_W, settings.BTN_H)
        self.btn = pygame.transform.scale(base, size)
        self.btn_hover = pygame.transform.scale(hover, size)
        pause_bg = img(PAUSE_BG_PATH)
        self.pause_bg = pygame.transform.scale(
            pause_bg, (settings.SCREEN_W, settings.SCREEN_H)
        )

    def _draw_objects(self, objects: list, cam: tuple[int, int]) -> None:
        pairs: list[tuple[pygame.Surface, pygame.Rect]] = []
        for obj in objects:
            image = getattr(obj, "image", None)
            rect_attr = getattr(obj, "rect", None)
            if image is not None and rect_attr is not None:
                rect = rect_attr() if callable(rect_attr) else rect_attr
                if isinstance(rect, pygame.Rect):
                    pairs.append((image, rect.move(-cam[0], -cam[1])))
                    continue
            obj.draw(self.surf, cam)
        if pairs:
            self.surf.blits(pairs)

    def draw_battle(self, game: "GameController") -> None:
        cam = game.cam
        self.surf.fill(BG_COLOR)
        game.map.draw(self.surf, cam, game.door_open)
        objs = (
            *game.wave_mgr.enemies,
            *game.effects,
            *game.pbul,
            *game.ebul,
            game.player,
        )
        if debug.SHOW_HITBOXES:
            for obj in objs:
                debug.draw_hitbox(self.surf, obj, cam)
            debug.draw_orbitals(self.surf, game.player, cam)
            for r in game.map.collides:
                debug.draw_hitbox(self.surf, r, cam)
            if not game.door_open:
                for r in game.map.door_collides:
                    debug.draw_hitbox(self.surf, r, cam)
        else:
            self._draw_objects(list(objs), cam)
        _draw_hud(self.surf, game.wave_mgr.wave, game.player.lives, self.heart)
        pygame.display.flip()

    def draw_pause(self, hovered_start: bool, hovered_exit: bool) -> tuple[pygame.Rect, pygame.Rect]:
        self.surf.blit(self.pause_bg, (0, 0))
        text = txt("PAUSED", PAUSE_TITLE_SIZE)
        self.surf.blit(
            text,
            (
                settings.SCREEN_W // 2 - text.get_width() // 2,
                settings.SCREEN_H // 2 - text.get_height() // 2 - settings.PAUSE_TEXT_OFF,
            ),
        )
        btn_w, btn_h = settings.BTN_W, settings.BTN_H
        start_btn = pygame.Rect(
            settings.SCREEN_W // 2 - btn_w // 2,
            settings.SCREEN_H // 2 - btn_h // 2,
            btn_w,
            btn_h,
        )
        exit_btn = pygame.Rect(
            settings.SCREEN_W // 2 - btn_w // 2,
            settings.SCREEN_H // 2 + settings.BTN_SPACING,
            btn_w,
            btn_h,
        )
        start_img = self.btn_hover if hovered_start else self.btn
        exit_img = self.btn_hover if hovered_exit else self.btn
        self.surf.blit(start_img, start_btn)
        self.surf.blit(exit_img, exit_btn)
        start_label = txt("RESUME", PAUSE_BTN_SIZE)
        exit_label = txt("MENU", PAUSE_BTN_SIZE)
        self.surf.blit(
            start_label,
            (
                start_btn.centerx - start_label.get_width() // 2,
                start_btn.centery - start_label.get_height() // 2,
            ),
        )
        self.surf.blit(
            exit_label,
            (
                exit_btn.centerx - exit_label.get_width() // 2,
                exit_btn.centery - exit_label.get_height() // 2,
            ),
        )
        pygame.display.flip()
        return start_btn, exit_btn

