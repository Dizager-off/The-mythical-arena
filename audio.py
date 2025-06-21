
from pathlib import Path
import pygame


ROOT = Path(__file__).resolve().parent / "assets" / "sfx"


def _load_sound(name: str) -> pygame.mixer.Sound:
    try:
        return pygame.mixer.Sound(str(ROOT / name))
    except pygame.error:
        print(f"Warning: failed to load sound '{name}'")
        return pygame.mixer.Sound(buffer=b"\0\0")


pygame.mixer.init()

BOW_VOLUME = 0.3
DOOR_OPEN_VOLUME = 0.4
KILL_ENEMY_VOLUME = 1.2
MAGE_ATTACK_VOLUME = 0.8
PICKUP_VOLUME = 0.6
BUTTON_VOLUME = 0.4


def _set_volume(sound: pygame.mixer.Sound, volume: float) -> None:
    sound.set_volume(volume)

BOW = _load_sound("Bow_attack.mp3")
_set_volume(BOW, BOW_VOLUME)
DOOR_OPEN = _load_sound("Door_open.mp3")
_set_volume(DOOR_OPEN, DOOR_OPEN_VOLUME)
KILL_ENEMY = _load_sound("Kill_Enemy.mp3")
_set_volume(KILL_ENEMY, KILL_ENEMY_VOLUME)
MAGE_ATTACK = _load_sound("Mage_attack.mp3")
_set_volume(MAGE_ATTACK, MAGE_ATTACK_VOLUME)
PICKUP = _load_sound("Pickup_upgrade.mp3")
_set_volume(PICKUP, PICKUP_VOLUME)
BUTTON = _load_sound("Button.mp3")
_set_volume(BUTTON, BUTTON_VOLUME)

