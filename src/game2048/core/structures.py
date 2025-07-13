from dataclasses import dataclass
from typing import Optional

import numpy as np
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel


@dataclass(slots=True, kw_only=True)
class Viewport:
	canvas: Optional[QPixmap] = None
	viewer: Optional[QLabel] = None


@dataclass(slots=True, kw_only=True)
class Frame:
	tick:           Optional[int] = None
	slide_tick:     Optional[int] = None
	emerge_tick:    Optional[int] = None
	movement:       Optional[str] = None
	previous:       Optional[np.ndarray] = None
	current:        Optional[np.ndarray] = None
	spawns:         Optional[list] = None
