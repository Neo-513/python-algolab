from itertools import product

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class C:
	class Anim:
		FRAME_COUNT = 10
		FRAME_INTERVAL = 15

		SPAWN_TILE_SCALES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
		MERGE_TILE_SCALES = [1.0, 1.1, 1.2, 1.3, 1.3, 1.3, 1.3, 1.2, 1.1, 1.0]

		SPAWN_TILE_SCALED_SIZES = []
		MERGE_TILE_SCALED_SIZES = []

	class GameStatus:
		CONTINUE    = 0
		WIN         = 1
		LOSE        = -1

	class Move:
		LEFT, RIGHT, UP, DOWN = "L", "R", "U", "D"
		ALL = (LEFT, DOWN, UP, RIGHT)
		KEYS = {
			Qt.Key.Key_Left:    LEFT,
			Qt.Key.Key_Right:   RIGHT,
			Qt.Key.Key_Up:      UP,
			Qt.Key.Key_Down:    DOWN
		}

	class BoardStyle:
		GRID_SIZE   = 4
		GRID_LAST   = GRID_SIZE - 1

		TILE_SIZE   = 100
		GAP_SIZE    = 15
		BOARD_SIZE  = TILE_SIZE * GRID_SIZE + GAP_SIZE * (GRID_SIZE + 1)

		BACKGROUND_COLOR    = QColor(187, 173, 160)
		EMPTY_TILE_COLOR    = QColor(205, 193, 180)

		COORDS = {}

	class FontStyle:
		FONT_SIZE   = 40

		FONT_COLOR_DARK     = QColor(119, 110, 101)
		FONT_COLOR_LIGHT    = QColor(249, 246, 242)

	class TileStyle:
		TILE_COLORS = []
		FONT_COLORS = []

	class TileValue:
		BASE    = 2
		COUNT   = 12
		EMPTY   = 0
		TARGET  = 11

	class TileSpawn:
		INITIAL_COUNT = 2

		VALUE_TWO   = 1
		VALUE_FOUR  = 2

		PROB_TWO    = 0.9
		PROB_FOUR   = 1 - PROB_TWO


C.Anim.SPAWN_TILE_SCALED_SIZES = [
	round(C.Anim.SPAWN_TILE_SCALES[i] * C.BoardStyle.TILE_SIZE) for i in range(C.Anim.FRAME_COUNT)
]
C.Anim.MERGE_TILE_SCALED_SIZES = [
	round(C.Anim.MERGE_TILE_SCALES[i] * C.BoardStyle.TILE_SIZE) for i in range(C.Anim.FRAME_COUNT)
]

C.BoardStyle.COORDS = {
	(i, j): (
		C.BoardStyle.TILE_SIZE * j + C.BoardStyle.GAP_SIZE * (j + 1),
		C.BoardStyle.TILE_SIZE * i + C.BoardStyle.GAP_SIZE * (i + 1)
	) for i, j in product(range(C.BoardStyle.GRID_SIZE), repeat=2)
}

C.TileStyle.TILE_COLORS = [
	C.BoardStyle.EMPTY_TILE_COLOR,  QColor(238, 228, 218),          QColor(237, 224, 200),
	QColor(242, 177, 121),          QColor(245, 149, 99),           QColor(246, 124, 95),
	QColor(246, 94, 59),            QColor(237, 207, 114),          QColor(237, 204, 97),
	QColor(237, 200, 80),           QColor(237, 197, 63),           QColor(237, 194, 46),
]
C.TileStyle.FONT_COLORS = [
	C.BoardStyle.EMPTY_TILE_COLOR,  C.FontStyle.FONT_COLOR_DARK,    C.FontStyle.FONT_COLOR_DARK,
	C.FontStyle.FONT_COLOR_LIGHT,   C.FontStyle.FONT_COLOR_LIGHT,   C.FontStyle.FONT_COLOR_LIGHT,
	C.FontStyle.FONT_COLOR_LIGHT,   C.FontStyle.FONT_COLOR_LIGHT,   C.FontStyle.FONT_COLOR_LIGHT,
	C.FontStyle.FONT_COLOR_LIGHT,   C.FontStyle.FONT_COLOR_LIGHT,   C.FontStyle.FONT_COLOR_LIGHT
]
