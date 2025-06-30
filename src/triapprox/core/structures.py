from dataclasses import dataclass
from typing import Optional

import numpy as np
import pyqtgraph as pg
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel


class Sched:
	@dataclass(slots=True, kw_only=True)
	class Stage:
		resolution: Optional[int] = None
		blur_kernel_size: Optional[int] = None
		advance_threshold: Optional[float] = None

	@dataclass(slots=True, kw_only=True)
	class Perturb:
		vertices: Optional[int] = None
		color: Optional[int] = None

	@dataclass(slots=True, kw_only=True)
	class Strategy:
		threshold: Optional[float] = None
		perturb: Optional["Sched.Perturb"] = None


class Opt:
	@dataclass(slots=True, kw_only=True)
	class Proposal:
		layer: Optional[int] = None
		patch: Optional[np.ndarray] = None
		vertices: Optional[np.ndarray] = None
		color: Optional[np.ndarray] = None
		texture: Optional[np.ndarray] = None
		mask: Optional[np.ndarray] = None
		invmask: Optional[np.ndarray] = None
		approx: Optional[np.ndarray] = None
		metric: Optional[float] = None

	@dataclass(slots=True, kw_only=True)
	class Accepted:
		vertices: Optional[np.ndarray] = None
		color: Optional[np.ndarray] = None
		texture: Optional[np.ndarray] = None
		mask: Optional[np.ndarray] = None
		invmask: Optional[np.ndarray] = None
		composite: Optional[np.ndarray] = None
		approx: Optional[np.ndarray] = None
		metric: Optional[float] = None

	@dataclass(slots=True, kw_only=True)
	class Snapshot:
		iteration: Optional[int] = None
		stage: Optional[int] = None
		metric: Optional[float] = None
		approx: Optional[bytes] = None


class Vis:
	@dataclass(slots=True, kw_only=True)
	class Trace:
		iterations: Optional[list[int]] = None
		metrics: Optional[list[float]] = None
		curve: Optional[pg.PlotDataItem] = None
		cursor: Optional[pg.TextItem] = None

	@dataclass(slots=True, kw_only=True)
	class Viewport:
		img_pool: Optional[dict[int, QImage]] = None
		view_pool: Optional[dict[int, np.ndarray]] = None
		canvas: Optional[QPixmap] = None
		ref_viewer: Optional[QLabel] = None
		approx_viewer: Optional[QLabel] = None
