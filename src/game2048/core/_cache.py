from itertools import product

import numpy as np
from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QFont, QPainter, QPixmap
from shared import util

from .constants import C


@util.graphic
def cache_graphic_background():
	pixmap = QPixmap(C.BoardStyle.BOARD_SIZE, C.BoardStyle.BOARD_SIZE)
	pixmap.fill(C.BoardStyle.BACKGROUND_COLOR)
	with QPainter(pixmap) as painter:
		rects = [QRect(*coord, C.BoardStyle.TILE_SIZE, C.BoardStyle.TILE_SIZE) for coord in C.BoardStyle.COORDS.values()]
		painter.setBrush(C.BoardStyle.EMPTY_TILE_COLOR)
		painter.setPen(Qt.PenStyle.NoPen)
		painter.drawRects(rects)
	pixmap.save("background.png")


@util.graphic
def cache_graphic_skeleton():
	pixmap = QPixmap(C.BoardStyle.BOARD_SIZE, C.BoardStyle.BOARD_SIZE)
	pixmap.fill(Qt.GlobalColor.transparent)
	pixmap.fill(C.BoardStyle.BACKGROUND_COLOR)
	with QPainter(pixmap) as painter:
		rects = [QRect(*coord, C.BoardStyle.TILE_SIZE, C.BoardStyle.TILE_SIZE) for coord in C.BoardStyle.COORDS.values()]
		painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
		painter.setBrush(Qt.GlobalColor.transparent)
		painter.setPen(Qt.PenStyle.NoPen)
		painter.drawRects(rects)
	pixmap.save("skeleton.png")


@util.graphic
def cache_graphic_atlas():
	pixmap = QPixmap(C.BoardStyle.TILE_SIZE * C.TileValue.COUNT, C.BoardStyle.TILE_SIZE)
	with QPainter(pixmap) as painter:
		for i, (tile_color, font_color) in enumerate(zip(C.TileStyle.TILE_COLORS, C.TileStyle.FONT_COLORS)):
			rect = C.BoardStyle.TILE_SIZE * i, 0, C.BoardStyle.TILE_SIZE, C.BoardStyle.TILE_SIZE
			painter.fillRect(*rect, tile_color)
			painter.setFont(QFont("", C.FontStyle.FONT_SIZE, QFont.Weight.Bold))
			painter.setPen(font_color)
			painter.drawText(*rect, Qt.AlignmentFlag.AlignCenter, str(C.TileValue.BASE ** i))
	pixmap.save("atlas.png")


def cache_heuristic_coalesce():
	coalesce = {"forward": {}, "reverse": {}}
	for tile_values in product(range(C.TileValue.COUNT), repeat=C.BoardStyle.GRID_SIZE):
		merged_tile_values = []
		has_merged = False

		for tile_value in tile_values:
			if tile_value == C.TileValue.EMPTY:
				continue
			if merged_tile_values and tile_value == merged_tile_values[-1] and not has_merged:
				merged_tile_values[-1] += 1
				has_merged = True
			else:
				merged_tile_values.append(tile_value)
				has_merged = False
		merged_tile_values += [C.TileValue.EMPTY] * (C.BoardStyle.GRID_SIZE - len(merged_tile_values))

		line = np.array(tile_values, dtype=np.uint8)
		coalesce["forward"][line.tobytes()]         = np.array(merged_tile_values, dtype=np.uint8)
		coalesce["reverse"][line[::-1].tobytes()]   = np.array(merged_tile_values, dtype=np.uint8)[::-1]
	util.write("coalesce.pkl", coalesce)


def cache_heuristic_evaluation():
	evaluation = {}
	for tile_values in product(range(C.TileValue.COUNT), repeat=C.BoardStyle.GRID_SIZE):
		line = np.array(tile_values, dtype=np.uint8)
		evaluation[line.tobytes()] = {
			"monotonicity": np.sum(line) if np.all(np.diff(tile_values) >= 0) or np.all(np.diff(tile_values) <= 0) else 0,
			"mergeability": np.sum(line[line != 0][:-1][np.diff(line[line != 0]) == 0])
		}
	util.write("evaluation.pkl", evaluation)


def cache_anim_trajectories():
	def pixel_of(pix):
		return pix * (C.BoardStyle.TILE_SIZE + C.BoardStyle.GAP_SIZE) + C.BoardStyle.GAP_SIZE

	def linear_interp(_src_pos, _dst_pos):
		(_src_row, _src_col), (_dst_row, _dst_col) = _src_pos, _dst_pos
		src_x, src_y = pixel_of(_src_col), pixel_of(_src_row)
		dst_x, dst_y = pixel_of(_dst_col), pixel_of(_dst_row)
		delta_x, delta_y = (dst_x - src_x), (dst_y - src_y)
		return [(round(src_x + delta_x * offset), round(src_y + delta_y * offset)) for offset in offsets]

	offsets = (np.arange(C.Anim.FRAME_COUNT) + 1) / C.Anim.FRAME_COUNT
	trajectories = {}

	for src_row, src_col, dst_row, dst_col in product(range(C.BoardStyle.GRID_SIZE), repeat=4):
		if src_row == dst_row or src_col == dst_col:
			src_pos, dst_pos = (src_row, src_col), (dst_row, dst_col)
			trajectories[src_pos, dst_pos] = linear_interp(src_pos, dst_pos)
	util.write("trajectories.pkl", trajectories)


def cache_anim_motions():
	coalesce = util.read(util.resource("coalesce.pkl"))
	motions = {}

	for serialized_previous, current in coalesce["forward"].items():
		motions[serialized_previous] = {"transfers": [], "fused": []}
		previous = np.frombuffer(serialized_previous, dtype=np.uint8).tolist()
		dst_col = 0

		for src_col in range(C.BoardStyle.GRID_SIZE):
			if previous[src_col] == 0:
				continue
			motions[serialized_previous]["transfers"].insert(0, (src_col, dst_col))

			if current[dst_col] == previous[src_col]:
				dst_col += 1
			else:
				current[dst_col] -= 1
				motions[serialized_previous]["fused"].append(dst_col)
	util.write("motions.pkl", motions)
