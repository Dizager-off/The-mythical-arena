
from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from .input_handler import InputHandler
from .game import GameController
from .shop import ShopController

__all__ = ["InputHandler", "GameController", "ShopController"]
