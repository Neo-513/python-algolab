import random

import numpy as np

from .constants import C
from .loader import HeuristicCache


def build():
	return np.zeros((C.BoardStyle.GRID_SIZE, C.BoardStyle.GRID_SIZE), dtype=np.uint8)


def initialize(grid):
	grid.fill(C.TileValue.EMPTY)
	return [spawn(grid) for _ in range(C.TileSpawn.INITIAL_COUNT)]


def move(grid, movement):
	if movement in (C.Move.LEFT, C.Move.UP):
		coalesce = HeuristicCache.COALESCE["forward"]
	elif movement in (C.Move.RIGHT, C.Move.DOWN):
		coalesce = HeuristicCache.COALESCE["reverse"]
	else:
		return

	if movement in (C.Move.LEFT, C.Move.RIGHT):
		for i in range(C.BoardStyle.GRID_SIZE):
			grid[i] = coalesce[grid[i].tobytes()]
	elif movement in (C.Move.UP, C.Move.DOWN):
		for i in range(C.BoardStyle.GRID_SIZE):
			grid.T[i] = coalesce[grid.T[i].tobytes()]
	else:
		return


def spawn(grid):
	empty_tile = tuple(random.choice(empty_tiles(grid)))
	grid[empty_tile] = C.TileSpawn.VALUE_TWO if random.random() <= C.TileSpawn.PROB_TWO else C.TileSpawn.VALUE_FOUR
	return empty_tile


def is_changed(previous, current):
	return not np.array_equal(previous, current)


def should_spawn(previous, current):
	return C.TileValue.EMPTY in current and is_changed(previous, current)


def is_win(grid):
	return C.TileValue.TARGET in grid


def is_lose(grid):
	if C.TileValue.EMPTY in grid:
		return False
	if np.any(grid[:, :-1] == grid[:, 1:]):
		return False
	if np.any(grid[:-1, :] == grid[1:, :]):
		return False
	return True


def empty_tiles(grid):
	return np.argwhere(grid == C.TileValue.EMPTY)


def empty_count(grid):
	return np.count_nonzero(grid == C.TileValue.EMPTY)


def is_full(grid):
	return C.TileValue.EMPTY not in grid


def corner_tiles(grid):
	return (
		grid[0, 0],
		grid[0, C.BoardStyle.GRID_LAST],
		grid[C.BoardStyle.GRID_LAST, 0],
		grid[C.BoardStyle.GRID_LAST, C.BoardStyle.GRID_LAST]
	)


def max_tile(grid):
	return np.max(grid)
