from dataclasses import dataclass
from multiprocessing import Queue
from typing import Optional

import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QLabel


@dataclass(slots=True)
class Trace:
	trace_id: Optional[int] = None
	queue: Optional[Queue] = None
	polygon_count: Optional[int] = None
	vertex_count: Optional[int] = None
	reference_pool: Optional[dict[int, np.ndarray]] = None
	canvas: Optional[QLabel] = None
	curve: Optional[pg.PlotDataItem] = None
	iterations: Optional[list[int]] = None
	metrics: Optional[list[float]] = None
	name: Optional[str] = None
	cursor: Optional[pg.TextItem] = None
	logs: Optional[list[list[str]]] = None
	dashboard: Optional[pg.TextItem] = None


@dataclass(slots=True)
class Proposal:
	layer: Optional[int] = None
	vertices: Optional[np.ndarray] = None
	patch: Optional[np.ndarray] = None
	color: Optional[np.ndarray] = None
	texture: Optional[np.ndarray] = None
	mask: Optional[np.ndarray] = None
	invmask: Optional[np.ndarray] = None
	approximation: Optional[np.ndarray] = None
	metric: Optional[float] = 0


@dataclass(slots=True)
class Accepted:
	resolution: Optional[int] = None
	vertices: Optional[np.ndarray] = None
	color: Optional[np.ndarray] = None
	texture: Optional[np.ndarray] = None
	mask: Optional[np.ndarray] = None
	invmask: Optional[np.ndarray] = None
	composite: Optional[np.ndarray] = None
	approximation: Optional[np.ndarray] = None
	metric: Optional[float] = 0


@dataclass(slots=True)
class Buffer:
	composite: Optional[np.ndarray] = None
