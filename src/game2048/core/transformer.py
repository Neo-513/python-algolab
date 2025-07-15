from .constants import C


def transform_forward(movement, grid):
	match movement:
		case C.Move.LEFT:   return grid
		case C.Move.RIGHT:  return grid[::-1, ::-1]
		case C.Move.UP:     return grid.T[::-1]
		case C.Move.DOWN:   return grid[::-1].T
	return None


def transform_backward(movement, pos):
	row, col = pos
	match movement:
		case C.Move.LEFT:   return row, col
		case C.Move.RIGHT:  return C.BoardStyle.GRID_LAST - row, C.BoardStyle.GRID_LAST - col
		case C.Move.UP:     return col, C.BoardStyle.GRID_LAST - row
		case C.Move.DOWN:   return C.BoardStyle.GRID_LAST - col, row
	return None
