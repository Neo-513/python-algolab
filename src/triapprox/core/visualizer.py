from dataclasses import dataclass
from functools import cache
from typing import Optional

import cv2
import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QImage, QPainter, QPixmap
from PyQt6.QtWidgets import QLabel

from .advancer import StageConfig
from .worker import Worker


@dataclass(slots=True, kw_only=True)
class Trace:
	iterations: Optional[list[int]] = None
	metrics: Optional[list[float]] = None
	curve: Optional[pg.PlotDataItem] = None
	cursor: Optional[pg.TextItem] = None


@dataclass(slots=True, kw_only=True)
class Viewport:
	image_pool: Optional[dict[int, QImage]] = None
	view_pool: Optional[dict[int, np.ndarray]] = None
	canvas: Optional[QPixmap] = None
	ref_viewer: Optional[QLabel] = None
	approx_viewer: Optional[QLabel] = None


class Builder:
	@staticmethod
	def build_trace(plot_widget):
		cursor = pg.TextItem(anchor=(-0.1, 1.1), color="y")
		plot_widget.addItem(cursor)
		plot_widget.setXRange(0, Worker.MAX_ITERATION)
		plot_widget.setYRange(0, 1)
		plot_widget.setInteractive(False)

		return Trace(
			iterations=[],
			metrics=[],
			curve=plot_widget.plot([], [], pen="y"),
			cursor=cursor
		)

	@staticmethod
	def build_viewport(ref_viewer, approx_viewer):
		image_pool, view_pool = {}, {}
		for stage in StageConfig.STAGES:
			res = stage.resolution
			image_pool[res] = QImage(res, res, QImage.Format.Format_RGB888)
			ptr = image_pool[res].bits()
			ptr.setsize(res * res * 3)
			view_pool[res] = np.ndarray((res, res, 3), dtype=np.uint8, buffer=ptr)

		return Viewport(
			image_pool=image_pool,
			view_pool=view_pool,
			canvas=QPixmap(StageConfig.FINAL_RESOLUTION, StageConfig.FINAL_RESOLUTION),
			ref_viewer=ref_viewer,
			approx_viewer=approx_viewer
		)


class Loader:
	@staticmethod
	@cache
	def load_reference_pool(ref_path, dtype=np.uint8):
		ref = cv2.imread(ref_path)
		reference_pool = {}
		for stage in StageConfig.STAGES:
			resized_ref = cv2.resize(ref, (stage.resolution, stage.resolution))
			blurred_ref = cv2.GaussianBlur(resized_ref, (stage.blur_kernel_size, stage.blur_kernel_size), 0)
			reference_pool[stage.resolution] = blurred_ref.astype(dtype)
		return reference_pool


class Renderer:
	@staticmethod
	def render_ref(viewport, data):
		resolution = StageConfig.FINAL_RESOLUTION
		np.copyto(viewport.view_pool[resolution], data[:, :, ::-1])
		with QPainter(viewport.canvas) as painter:
			painter.drawImage(QRect(0, 0, resolution, resolution), viewport.image_pool[resolution])
		viewport.ref_viewer.setPixmap(viewport.canvas)

	@staticmethod
	def render_approx(viewport, data, resolution):
		data = np.frombuffer(data, dtype=np.uint8).reshape(resolution, resolution, 3)
		np.copyto(viewport.view_pool[resolution], data[:, :, ::-1])
		with QPainter(viewport.canvas) as painter:
			rect = QRect(0, 0, StageConfig.FINAL_RESOLUTION, StageConfig.FINAL_RESOLUTION)
			painter.drawImage(rect, viewport.image_pool[resolution])
		viewport.approx_viewer.setPixmap(viewport.canvas)


class Refresher:
	@staticmethod
	def refresh_plot(trace, snapshot):
		trace.iterations.append(snapshot.iteration)
		trace.metrics.append(snapshot.metric)
		trace.curve.setData(trace.iterations, trace.metrics)
		trace.cursor.setText(f"ssim={snapshot.metric:.4f}")
		trace.cursor.setPos(trace.iterations[-1], trace.metrics[-1])

	@staticmethod
	def refresh_canvas(viewport, snapshot):
		if snapshot.approximation:
			Renderer.render_approx(viewport, snapshot.approximation, StageConfig.STAGES[snapshot.stage].resolution)
