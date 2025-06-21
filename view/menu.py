from __future__ import annotations

from pathlib import Path
import pygame
import sys

import audio
import music

import settings
from settings import FPS, txt, img, BTN_W, BTN_H, BTN_SPACING, MENU_TITLE_OFF
TITLE_SIZE = 60
BTN_LABEL_SIZE = 38
from controller.game import GameController


class Menu:

    def __init__(self, surf: pygame.Surface):
        self.surf = surf
        bg = img(Path("assets/UI/background/Menu.png"))
        self.bg = pygame.transform.scale(bg, (settings.SCREEN_W, settings.SCREEN_H))
        base = img(Path("assets/UI/button/button.png"))
        hover = img(Path("assets/UI/button/button_hover.png"))
        size = (BTN_W, BTN_H)
        self.btn = pygame.transform.scale(base, size)
        self.btn_hover = pygame.transform.scale(hover, size)

    def loop(self) -> None:
        clock = pygame.time.Clock()
        music.play(music.MAIN_MENU, music.MAIN_MENU_VOLUME)
        hovered_start = hovered_exit = False
        while True:
            clock.tick(FPS)
            self.surf.blit(self.bg, (0, 0))
            title = txt("The mythical arena", TITLE_SIZE)
            self.surf.blit(
                title,
                (
                    settings.SCREEN_W // 2 - title.get_width() // 2,
                    settings.SCREEN_H // 2 - MENU_TITLE_OFF,
                ),
            )
            btn_w, btn_h = BTN_W, BTN_H
            start_btn = pygame.Rect(
                settings.SCREEN_W // 2 - btn_w // 2,
                settings.SCREEN_H // 2 - btn_h // 2,
                btn_w,
                btn_h,
            )
            exit_btn = pygame.Rect(
                settings.SCREEN_W // 2 - btn_w // 2,
                settings.SCREEN_H // 2 + BTN_SPACING,
                btn_w,
                btn_h,
            )
            mouse = pygame.mouse.get_pos()
            start_img = self.btn
            exit_img = self.btn
            if start_btn.collidepoint(mouse):
                if not hovered_start:
                    audio.BUTTON.play()
                hovered_start = True
                start_img = self.btn_hover
            else:
                hovered_start = False
            if exit_btn.collidepoint(mouse):
                if not hovered_exit:
                    audio.BUTTON.play()
                hovered_exit = True
                exit_img = self.btn_hover
            else:
                hovered_exit = False
            self.surf.blit(start_img, start_btn)
            self.surf.blit(exit_img, exit_btn)
            start_label = txt("START", BTN_LABEL_SIZE)
            exit_label = txt("EXIT", BTN_LABEL_SIZE)
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
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if start_btn.collidepoint(e.pos):
                        GameController(self.surf).loop()
                        music.play(music.MAIN_MENU, music.MAIN_MENU_VOLUME)
                    elif exit_btn.collidepoint(e.pos):
                        pygame.quit(); sys.exit()
