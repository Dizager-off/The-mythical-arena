from __future__ import annotations
import sys
import pygame
import audio
from settings import FPS
from .renderer import Renderer


def pause_menu(renderer: Renderer, clock: pygame.time.Clock) -> bool:
    hovered_start = hovered_exit = False
    paused = True
    while paused:
        clock.tick(FPS)
        start_btn, exit_btn = renderer.draw_pause(hovered_start, hovered_exit)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos):
                    paused = False
                if exit_btn.collidepoint(event.pos):
                    return True
        mouse = pygame.mouse.get_pos()
        if start_btn.collidepoint(mouse):
            if not hovered_start:
                audio.BUTTON.play()
            hovered_start = True
        else:
            hovered_start = False
        if exit_btn.collidepoint(mouse):
            if not hovered_exit:
                audio.BUTTON.play()
            hovered_exit = True
        else:
            hovered_exit = False
    return False
