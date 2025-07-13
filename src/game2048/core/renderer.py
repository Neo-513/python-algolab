from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter

from . import transformer
from .constants import C
from .loader import AnimCache, GraphicCache


def render_static_frame(viewport):
	with QPainter(viewport.canvas) as painter:
		painter.drawPixmap(0, 0, GraphicCache.BACKGROUND)
	viewport.viewer.setPixmap(viewport.canvas)


def render_slide_frame(viewport, frame):
	transformed_grid = transformer.transform_forward(frame.movement, frame.previous)
	with QPainter(viewport.canvas) as painter:
		for row in range(C.BoardStyle.GRID_SIZE):
			for src_col, dst_col in AnimCache.MOTIONS[transformed_grid[row].tobytes()]["transfers"]:
				src_pos = transformer.transform_backward(frame.movement, (row, src_col))
				dst_pos = transformer.transform_backward(frame.movement, (row, dst_col))
				pos = frame.previous[src_pos]
				coord = AnimCache.TRAJECTORIES[src_pos, dst_pos][frame.tick]
				painter.drawPixmap(*coord, GraphicCache.TILES[pos])
	viewport.viewer.setPixmap(viewport.canvas)


def render_spawn_frame(viewport, frame):
	with QPainter(viewport.canvas) as painter:
		for pos in frame.spawns:
			render_scaled_tile(frame, painter, pos, C.Anim.SPAWN_TILE_SCALED_SIZES)
	viewport.viewer.setPixmap(viewport.canvas)


def render_merge_frame(viewport, frame):
	with QPainter(viewport.canvas) as painter:
		painter.drawPixmap(0, 0, GraphicCache.SKELETON)
		transformed_grid = transformer.transform_forward(frame.movement, frame.previous)
		for row, line in enumerate(transformed_grid):
			for col in AnimCache.MOTIONS[line.tobytes()]["fused"]:
				pos = transformer.transform_backward(frame.movement, (row, col))
				render_scaled_tile(frame, painter, pos, C.Anim.MERGE_TILE_SCALED_SIZES)
	viewport.viewer.setPixmap(viewport.canvas)


def render_scaled_tile(frame, painter, pos, tile_scaled_sizes):
	scaled_tile_size = tile_scaled_sizes[frame.tick]
	scaled_tile = GraphicCache.TILES[frame.current[pos]].scaled(
		scaled_tile_size, scaled_tile_size,
		Qt.AspectRatioMode.IgnoreAspectRatio,
		Qt.TransformationMode.FastTransformation
	)

	offset = (C.BoardStyle.TILE_SIZE - scaled_tile_size) // 2
	coord = tuple(c + offset for c in C.BoardStyle.COORDS[pos])
	painter.drawPixmap(*coord, scaled_tile)
