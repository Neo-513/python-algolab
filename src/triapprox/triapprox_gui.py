import sys

import pyqtgraph as pg
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow
from shared import util

from core.advancer import StageConfig
from core.visualizer import Builder, Loader, Refresher, Renderer
from core.worker import Worker
from ui.gui_ui import Ui_MainWindow


class Gui(QMainWindow, Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)

		self.setWindowIcon(QIcon(f"{util.RESOURCE}/logo"))
		self.radioButton_monalisa.clicked.connect(lambda: self.on_radio_clicked(self.radioButton_monalisa, "mona_lisa"))
		self.radioButton_firefox.clicked.connect(lambda: self.on_radio_clicked(self.radioButton_firefox, "firefox"))
		self.radioButton_darwin.clicked.connect(lambda: self.on_radio_clicked(self.radioButton_darwin, "darwin"))
		self.radioButton_custom.clicked.connect(lambda: self.on_radio_clicked(self.radioButton_custom, "custom"))
		util.buttonize(self.pushButton, self.on_button_clicked, f"{util.RESOURCE}/start")

		plot_widget = pg.PlotWidget()
		self.groupBox_plot.layout().addWidget(plot_widget)
		self.trace = Builder.build_trace(plot_widget)
		self.viewport = Builder.build_viewport(self.label_ref, self.label_approx)

		self.is_running = False
		self.timer = util.ticker(self.pushButton)
		self.worker = self.reference_pool = self.selected_radio = None
		self.radioButton_monalisa.click()

	def on_radio_clicked(self, radio, ref_name):
		if ref_name == "custom":
			ref_path = QFileDialog.getOpenFileName(filter="*.png")[0]
		else:
			ref_path = f"{util.RESOURCE}/{ref_name}.png"

		if ref_path:
			self.reference_pool = Loader.load_reference_pool(ref_path)
			Renderer.render_ref(self.viewport, self.reference_pool[StageConfig.FINAL_RESOLUTION])
			self.selected_radio = radio
		else:
			self.selected_radio.click()

	def on_button_clicked(self):
		if self.is_running:
			self.stop_optimization()
		else:
			self.start_optimization()

	def start_optimization(self):
		self.is_running = True
		self.frame.setEnabled(False)

		self.trace.iterations.clear()
		self.trace.metrics.clear()
		self.trace.curve.clear()

		self.worker = Worker(self.reference_pool)
		self.worker.snapshot_ready.connect(lambda snapshot: Refresher.refresh_plot(self.trace, snapshot))
		self.worker.snapshot_ready.connect(lambda snapshot: Refresher.refresh_canvas(self.viewport, snapshot))
		self.worker.start()

		self.pushButton.setIcon(QIcon(f"{util.RESOURCE}/stop"))
		self.pushButton.setText("00:00:00")
		self.timer.second = 0
		self.timer.start()

	def stop_optimization(self):
		self.is_running = False
		self.timer.stop()
		self.pushButton.setIcon(QIcon(f"{util.RESOURCE}/start"))
		self.worker.shutdown()
		self.frame.setEnabled(True)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	gui = Gui()
	gui.setFixedSize(gui.window().size())
	gui.show()
	sys.exit(app.exec())
