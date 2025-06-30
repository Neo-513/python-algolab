from functools import cache

import cv2
import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QImage, QPainter, QPixmap

from . import constants
from .structures import Vis


class Builder:
	@staticmethod
	def build_trace(plot_widget):
		cursor = pg.TextItem(anchor=(-0.1, 1.1), color="y")
		plot_widget.addItem(cursor)
		plot_widget.setXRange(0, constants.MAX_ITERATION)
		plot_widget.setYRange(0, 1)
		plot_widget.setInteractive(False)

		return Vis.Trace(
			iterations=[],
			metrics=[],
			curve=plot_widget.plot([], [], pen="y"),
			cursor=cursor
		)

	@staticmethod
	def build_viewport(ref_viewer, approx_viewer):
		img_pool, view_pool = {}, {}
		for stage in constants.STAGES:
			img_pool[stage.resolution] = QImage(stage.resolution, stage.resolution, QImage.Format.Format_RGB888)
			ptr = img_pool[stage.resolution].bits()
			ptr.setsize(stage.resolution * stage.resolution * 3)
			view_pool[stage.resolution] = np.ndarray((stage.resolution, stage.resolution, 3), dtype=np.uint8, buffer=ptr)

		return Vis.Viewport(
			img_pool=img_pool,
			view_pool=view_pool,
			canvas=QPixmap(constants.FINAL_RESOLUTION, constants.FINAL_RESOLUTION),
			ref_viewer=ref_viewer,
			approx_viewer=approx_viewer
		)


class Loader:
	@staticmethod
	@cache
	def load_ref_pool(ref_path):
		ref = cv2.imread(ref_path)
		ref_pool = {}
		for stage in constants.STAGES:
			resized_ref = cv2.resize(ref, (stage.resolution, stage.resolution))
			blurred_ref = cv2.GaussianBlur(resized_ref, (stage.blur_kernel_size, stage.blur_kernel_size), 0)
			ref_pool[stage.resolution] = blurred_ref.astype(np.uint8)
		return ref_pool


class Renderer:
	@staticmethod
	def render(viewport, data, resolution=constants.FINAL_RESOLUTION, is_ref=True):
		if not is_ref:
			data = np.frombuffer(data, dtype=np.uint8).reshape(resolution, resolution, 3)
		np.copyto(viewport.view_pool[resolution], data[..., ::-1])
		viewport.canvas.fill(Qt.GlobalColor.transparent)
		with QPainter(viewport.canvas) as painter:
			rect = QRect(0, 0, constants.FINAL_RESOLUTION, constants.FINAL_RESOLUTION)
			painter.drawImage(rect, viewport.img_pool[resolution])
		(viewport.ref_viewer if is_ref else viewport.approx_viewer).setPixmap(viewport.canvas)


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
		if snapshot.approx:
			Renderer.render(viewport, snapshot.approx, resolution=snapshot.stage.resolution, is_ref=False)
