from functools import lru_cache

from PyQt6.QtGui import QPixmap
from shared import util

from .constants import C


@lru_cache
@util.graphic
def load_graphic_background():
	return QPixmap(util.resource("background.png"))


@lru_cache
@util.graphic
def load_graphic_skeleton():
	return QPixmap(util.resource("skeleton.png"))


@lru_cache
@util.graphic
def load_graphic_tiles():
	atlas = QPixmap(util.resource("atlas.png"))
	return {
		i: atlas.copy(
			C.BoardStyle.TILE_SIZE * i, 0, C.BoardStyle.TILE_SIZE, C.BoardStyle.TILE_SIZE
		) for i in range(C.TileValue.COUNT)
	}


@lru_cache
def load_heuristic_coalesce():
	return util.read(util.resource("coalesce.pkl"))


@lru_cache
def load_heuristic_evaluation():
	return util.read(util.resource("evaluation.pkl"))


@lru_cache
def load_anim_trajectories():
	return util.read(util.resource("trajectories.pkl"))


@lru_cache
def load_anim_motions():
	return util.read(util.resource("motions.pkl"))


class GraphicCache:
	BACKGROUND      = load_graphic_background()
	SKELETON        = load_graphic_skeleton()
	TILES           = load_graphic_tiles()


class HeuristicCache:
	COALESCE        = load_heuristic_coalesce()
	EVALUATION      = load_heuristic_evaluation()


class AnimCache:
	TRAJECTORIES    = load_anim_trajectories()
	MOTIONS         = load_anim_motions()
