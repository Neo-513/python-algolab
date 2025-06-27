import sys
from functools import cache

import cv2
import numpy as np
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow
from shared import util

from core import phase
from core.runner import Runner
from core.visualizer import Visualizer
from ui.gui_ui import Ui_MainWindow


class Gui(QMainWindow, Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)

		self.setWindowIcon(QIcon(f"{util.RESOURCE}/logo"))
		self.radioButton_monalisa.clicked.connect(lambda: self.ref_select("mona_lisa"))
		self.radioButton_firefox.clicked.connect(lambda: self.ref_select("firefox"))
		self.radioButton_darwin.clicked.connect(lambda: self.ref_select("darwin"))
		self.radioButton_custom.clicked.connect(lambda: self.ref_select("custom"))
		self.checkBox_0.clicked.connect(lambda is_visible: self.viz_toggle(is_visible, 0))
		self.checkBox_1.clicked.connect(lambda is_visible: self.viz_toggle(is_visible, 1))
		self.checkBox_2.clicked.connect(lambda is_visible: self.viz_toggle(is_visible, 2))
		util.fill(self.label_ref, create=True)
		util.fill(self.label_approx0, create=True)
		util.fill(self.label_approx1, create=True)
		util.fill(self.label_approx2, create=True)
		util.buttonize(self.pushButton, self.run_toggle, f"{util.RESOURCE}/start")

		self.is_running = False
		self.visualizer = Visualizer(self.groupBox_plot, self)
		self.runner = Runner(self.visualizer)
		self.elapsed_timer = util.ticker(self.pushButton)
		self.polling_timer = util.poller(15, self.runner.poll)

	def ref_select(self, name):
		util.fill(self.label_ref)
		util.fill(self.label_approx0)
		util.fill(self.label_approx1)
		util.fill(self.label_approx2)

		path = QFileDialog.getOpenFileName(filter="*.png")[0] if name == "custom" else f"{util.RESOURCE}/{name}.png"
		if path:
			self.visualizer.reference_pool = self.ref_load(path)
			self.visualizer.render(self.label_ref)
		else:
			self.visualizer.reference_pool = None

	@staticmethod
	@cache
	def ref_load(path, dtype=np.uint8):
		reference = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
		reference_pool = {}
		for stage in phase.STAGES:
			resized_reference = cv2.resize(reference, (stage.resolution, stage.resolution))
			blurred_reference = cv2.GaussianBlur(resized_reference, (stage.blur_kernel_size, stage.blur_kernel_size), 0)
			reference_pool[stage.resolution] = blurred_reference.astype(dtype)
		return reference_pool

	def run_toggle(self):
		if not self.visualizer.reference_pool:
			return util.popup("请选择图片", f"{util.RESOURCE}/error")
		if self.is_running:
			self.run_stop()
		else:
			self.run_start()

	def run_start(self):
		self.is_running = True
		self.frame_radio.setEnabled(False)
		self.visualizer.clear()
		self.runner.spawn()
		self.pushButton.setIcon(QIcon(f"{util.RESOURCE}/stop"))
		self.pushButton.setText("00:00:00")
		self.elapsed_timer.second = 0
		self.elapsed_timer.start()
		self.polling_timer.start()

	def run_stop(self):
		self.is_running = False
		self.polling_timer.stop()
		self.elapsed_timer.stop()
		self.pushButton.setIcon(QIcon(f"{util.RESOURCE}/start"))
		self.runner.shutdown()
		self.frame_radio.setEnabled(True)

	def viz_toggle(self, is_visible, trace_id):
		self.visualizer.traces[trace_id].tracer.chart_curve.setVisible(is_visible)
		self.visualizer.traces[trace_id].tracer.chart_cursor.setVisible(is_visible)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	gui = Gui()
	gui.setFixedSize(gui.window().size())
	gui.show()
	sys.exit(app.exec())
