from functools import lru_cache
from itertools import product

import numpy as np

from . import engine
from .constants import C
from .loader import HeuristicCache

SHALLOW_SEARCH_DEPTHS   = [3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2]
DEEP_SEARCH_DEPTHS      = [5, 5, 5, 4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2]

SCORE_WIN   = 10000
SCORE_LOSE  = -10000

PROBS = [{
	C.TileSpawn.VALUE_TWO:      0,
	C.TileSpawn.VALUE_FOUR:     0
}] + [{
	C.TileSpawn.VALUE_TWO:      round(C.TileSpawn.PROB_TWO / i, 4),
	C.TileSpawn.VALUE_FOUR:     round(C.TileSpawn.PROB_FOUR / i, 4)
} for i in range(1, C.BoardStyle.GRID_SIZE ** 2)]


def decide(grid):
	search_depths = SHALLOW_SEARCH_DEPTHS if engine.max_tile(grid) <= 8 else DEEP_SEARCH_DEPTHS
	max_depth = search_depths[engine.empty_count(grid)]
	movement, _ = search(grid.tobytes(), 0, max_depth)
	return movement


@lru_cache(maxsize=1_000_000)
def search(serialized_grid, depth, max_depth):
	grid = np.frombuffer(serialized_grid, dtype=np.uint8).reshape((C.BoardStyle.GRID_SIZE, C.BoardStyle.GRID_SIZE))
	if engine.is_win(grid):
		return None, SCORE_WIN
	if engine.is_lose(grid):
		return None, SCORE_LOSE
	if depth >= max_depth:
		return None, evaluate(grid)

	if depth % 2 == 0:
		return search_max_node(grid, depth, max_depth)
	else:
		return search_chance_node(grid, depth, max_depth)


def search_max_node(grid, depth, max_depth):
	best_movement, best_score = None, -np.inf
	current = np.zeros_like(grid)

	for movement in C.Move.ALL:
		current[:] = grid
		engine.move(current, movement)
		if engine.is_changed(grid, current):
			_, score = search(current.tobytes(), depth + 1, max_depth)
			if score > best_score:
				best_movement, best_score = movement, score
	return best_movement, best_score


def search_chance_node(grid, depth, max_depth):
	if engine.is_full(grid):
		return None, evaluate(grid)

	empty_tiles = engine.empty_tiles(grid)
	probs = PROBS[len(empty_tiles)]
	score = 0
	current = np.zeros_like(grid)

	for empty_tile, (tile_value, prob) in product(empty_tiles, probs.items()):
		current[:] = grid
		current[tuple(empty_tile)] = tile_value
		_, s = search(current.tobytes(), depth + 1, max_depth)
		score += prob * s
	return None, score


def evaluate(grid):
	monotonicity = 0
	mergeability = 0

	row_bytes = grid.tobytes()
	col_bytes = grid.T.tobytes()

	for i in range(C.BoardStyle.GRID_SIZE):
		piece = slice(i * C.BoardStyle.GRID_SIZE, (i + 1) * C.BoardStyle.GRID_SIZE)
		evaluation_row = HeuristicCache.EVALUATION[row_bytes[piece]]
		evaluation_col = HeuristicCache.EVALUATION[col_bytes[piece]]
		monotonicity += evaluation_row["monotonicity"] + evaluation_col["monotonicity"]
		mergeability += evaluation_row["mergeability"] + evaluation_col["mergeability"]

	return (
		3.0 * engine.empty_count(grid) +
		2.0 * monotonicity +
		5.0 * (engine.max_tile(grid) in engine.corner_tiles(grid)) +
		1.5 * mergeability
	)
