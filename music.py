from __future__ import annotations

from pathlib import Path
import pygame

ROOT = Path(__file__).resolve().parent / "assets" / "music"


MAIN_MENU = ROOT / "Main menu.mp3"
BATTLE_1_2 = ROOT / "Battle Theme 1-2.mp3"
BATTLE_3_10 = ROOT / "Battle Theme 3-10.mp3"
SHOP = ROOT / "Shop.mp3"


MAIN_MENU_VOLUME = 0.4
BATTLE_1_2_VOLUME = 0.05
BATTLE_3_10_VOLUME = 0.2
SHOP_VOLUME = 0.2


def play(track: Path, volume: float) -> None:
    pygame.mixer.music.load(track.as_posix())
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)
