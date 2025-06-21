from __future__ import annotations

import math
from pathlib import Path
import pygame

pygame.init()

SCREEN_W, SCREEN_H = 1_400, 800


def set_fullscreen() -> pygame.Surface:

    surf = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    info = pygame.display.Info()
    global SCREEN_W, SCREEN_H, SPAWN_MIN_DIST
    SCREEN_W, SCREEN_H = info.current_w, info.current_h
    SPAWN_MIN_DIST = math.hypot(SCREEN_W, SCREEN_H)
    return surf


MAP_SCALE = 4 * 0.8


WORLD_W, WORLD_H = 4_096, 3_276
CAPTION = "The mythical arena"
FPS = 60

WHITE = (255, 255, 255)
BG_COLOR = (39, 32, 30)
RED, BLUE = (255, 0, 0), (0, 0, 255)
YELLOW, ORANGE = (255, 255, 0), (255, 165, 0)

PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_BULLET_SPEED = 7
PLAYER_FIRE_DELAY = 300
INVINCIBILITY = 1_000



PLAYER_SPRITE_Y_OFFSET = -16
SPAWN_MIN_DIST = math.hypot(SCREEN_W, SCREEN_H)
SPAWN_RANGE = 200
EXTRA_BULLET_SEP = 3

ORBITAL_SIZE = 50

ORBITAL_HITBOX = int(ORBITAL_SIZE * 0.6)
ORBITAL_RADIUS = 240
ORBITAL_SPEED = 0.04
HEART_SCALE = 3.0
SPAWN_HAZE = 210
TOTAL_WAVES = 4
TICKET = {"slime": 1, "wasp": 2, "zombie_archer": 3}
ENEMY_UPDATE_MARGIN = 200
WAVE_SPAWN_DELAY = 400
WAVE_SPAWN_BATCH = 3
BOW_ANGLE_STEP = 10


BTN_W, BTN_H = 265, 135
BTN_SPACING = 120
MENU_TITLE_OFF = 300
PAUSE_TEXT_OFF = 500
REWARD_SIZE = 40
REWARD_BULLET_OFF = 160
REWARD_LIFE_OFF = 20
REWARD_ORB_OFF = 120
PLAYER_SPAWN_OFF = 60
REWARD_TEXT_XOFF = 140
REWARD_TEXT_Y = 100
SPAWN_Y_OFF = 150
SPAWN_TRIES = 100
WAVE_BUDGET_BASE = 25
WAVE_BUDGET_GROWTH = 1.5
ARCHER_CAP = 10

_font_cache: dict[int, pygame.font.Font] = {}
_font_path = Path(__file__).resolve().parent / "assets" / "UI" / "font" / "pixel-font.ttf"

def txt(text: str, size: int, color: tuple[int, int, int] = WHITE) -> pygame.Surface:
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(_font_path.as_posix(), size)
    return _font_cache[size].render(text, True, color)

_image_cache: dict[Path, pygame.Surface] = {}


def img(path: Path) -> pygame.Surface:
    if path not in _image_cache:
        loaded = pygame.image.load(path.as_posix())
        if pygame.display.get_surface():
            loaded = loaded.convert_alpha()
        _image_cache[path] = loaded
    return _image_cache[path]

clamp = lambda v, lo, hi: max(lo, min(v, hi))
