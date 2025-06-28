from dataclasses import dataclass
from multiprocessing import Queue
from typing import Optional

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QImage, QPainter, QPixmap
from PyQt6.QtWidgets import QLabel

from .advancer import FINAL_RESOLUTION, STAGES
from .runner import MAX_ITERATION, STRATEGIES

CURVE_COLORS = ("r", "g", "y")

@dataclass(slots=True, kw_only=True)
class Tracer:
	display: Optional[QLabel] = None
	chart_curve: Optional[pg.PlotDataItem] = None
	chart_cursor: Optional[pg.TextItem] = None
	log_console: Optional[pg.TextItem] = None
	log_status: Optional[list[list[str]]] = None


@dataclass(slots=True, kw_only=True)
class Trace:
	trace_id: Optional[int] = None
	queue: Optional[Queue] = None
	iterations: Optional[list[int]] = None
	metrics: Optional[list[float]] = None
	tracer: Optional[Tracer] = None


class Visualizer:
	def __init__(self, group_box_plot, self1):
		self.traces = []
		self.reference_pool = None
		self.canvas = QPixmap(FINAL_RESOLUTION, FINAL_RESOLUTION)
		self.rect = QRect(0, 0, self.canvas.width(), self.canvas.height())
		self.image_pool = {}
		self.ptr_pool = {}
		self.view_pool = {}
		self.build(group_box_plot, self1)



	def build(self, group_box_plot, self1):
		plot_widget = pg.PlotWidget()
		plot_widget.setXRange(0, MAX_ITERATION)
		plot_widget.setYRange(0, 1)
		plot_widget.addLegend(offset=(-20, 10))
		plot_widget.setInteractive(False)
		group_box_plot.layout().addWidget(plot_widget)

		log_status = [[log] + ["0"] * len(STRATEGIES) for log in ["iteration:", "resolution:", "ssim:"]]
		log_console = pg.TextItem(anchor=(-0.8, 1.2))
		plot_widget.addItem(log_console)

		for i in range(len(STRATEGIES[:1])):
			tracer = Tracer(
				display=getattr(self1, f"label_approx{i}"),
				chart_curve=plot_widget.plot([], [], pen=CURVE_COLORS[i], name=f"拟合{i + 1}"),
				chart_cursor=pg.TextItem(anchor=(0, 1), color=CURVE_COLORS[i]),
				log_console=log_console,
				log_status=log_status
			)
			trace = Trace(
				trace_id=i,
				tracer=tracer,
				iterations=[],
				metrics=[],
				queue=Queue()
			)
			self.traces.append(trace)
			plot_widget.addItem(tracer.chart_cursor)

		for stage in STAGES:
			res = stage.resolution
			self.image_pool[res] = QImage(res, res, QImage.Format.Format_RGB888)
			self.ptr_pool[res] = self.image_pool[res].bits()
			self.ptr_pool[res].setsize(res * res * 3)
			self.view_pool[res] = np.ndarray((res, res, 3), dtype=np.uint8, buffer=self.ptr_pool[res])

	def refresh(self, trace, snapshot):

		trace.iterations.append(snapshot.iteration)
		trace.metrics.append(snapshot.metric)
		trace.tracer.chart_curve.setData(trace.iterations, trace.metrics)


		trace.tracer.chart_cursor.setText(f"{snapshot.metric:.4f}")
		trace.tracer.chart_cursor.setPos(trace.iterations[-1], trace.metrics[-1])

		if snapshot.approximation is not None:
			self.render(trace.tracer.display, img_data=snapshot.approximation, resolution=STAGES[snapshot.stage].resolution)

		trace.tracer.log_status[0][trace.trace_id + 1] = f"{snapshot.iteration}"
		trace.tracer.log_status[1][trace.trace_id + 1] = f"{STAGES[snapshot.stage].resolution}"
		trace.tracer.log_status[2][trace.trace_id + 1] = f"{snapshot.metric:.4f}"
		trace.tracer.log_console.setText("\n".join("\t".join(log) for log in trace.tracer.log_status))

		# 	f"coord_pert\t{self.approximation_thread.approximator.perturbation[0]}\n"
		# 	f"color_pert\t{self.approximation_thread.approximator.perturbation[1]}"

	def render(self, display, img_data=None, resolution=FINAL_RESOLUTION):
		if img_data is None:
			img_data = self.reference_pool[FINAL_RESOLUTION]
		else:
			img_data = np.frombuffer(img_data, dtype=np.uint8).reshape(resolution, resolution, 3)

		np.copyto(self.view_pool[resolution], img_data)
		with QPainter(self.canvas) as painter:
			painter.drawImage(self.rect, self.image_pool[resolution])
		display.setPixmap(self.canvas)


	def clear(self):
		for trace in self.traces:
			trace.iterations.clear()
			trace.metrics.clear()
			trace.tracer.chart_curve.clear()
