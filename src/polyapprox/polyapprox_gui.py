import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow
from shared import util

from core import loader, orchestrator, renderer,visual
from ui.gui_ui import Ui_MainWindow


class Gui(QMainWindow, Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		self.setWindowIcon(QIcon(f"{util.RESOURCE}/logo"))

		self.radioButton_monalisa.clicked.connect(lambda: self.switch("mona_lisa"))
		self.radioButton_firefox.clicked.connect(lambda: self.switch("firefox"))
		self.radioButton_darwin.clicked.connect(lambda: self.switch("darwin"))
		self.radioButton_custom.clicked.connect(lambda: self.switch("custom"))
		self.checkBox_0.clicked.connect(lambda state: self.show_curve(state, 0))
		self.checkBox_1.clicked.connect(lambda state: self.show_curve(state, 1))
		self.checkBox_2.clicked.connect(lambda state: self.show_curve(state, 2))
		util.buttonize(self.pushButton, self.approximate, f"{util.RESOURCE}/start")

		self.traces = visual.build(self.groupBox_plot, self)

		self.is_running = False
		self.elapsed_timer = util.elapsed(self.pushButton)
		self.polling_timer = util.qtimer(50, lambda: orchestrator.collect(self.traces))
		self.reference_pools, self.reference_pool = loader.load_reference_pools(), None
		self.radioButton_monalisa.click()

	def show_curve(self, state, trace_id):
		self.traces[trace_id].curve.setVisible(state)
		self.traces[trace_id].cursor.setVisible(state)

	def switch(self, reference_name):
		self.reference_pool = None
		util.fill(self.label_reference)
		util.fill(self.label_approx0)
		util.fill(self.label_approx1)
		util.fill(self.label_approx2)

		if reference_name == "custom":
			reference_path = QFileDialog.getOpenFileName(filter="*.png")[0]
			if not reference_path:
				return
			self.reference_pool = loader.load_reference_pool(reference_path)
		else:
			self.reference_pool = self.reference_pools[reference_name]
		renderer.render_reference(self.label_reference, self.reference_pool)


	def approximate(self):
		if not self.reference_pool:
			return util.prompt("请选择图片", "error")

		self.is_running = not self.is_running
		self.radioButton_monalisa.setDisabled(self.is_running)
		self.radioButton_firefox.setDisabled(self.is_running)
		self.radioButton_darwin.setDisabled(self.is_running)
		self.radioButton_custom.setDisabled(self.is_running)

		if self.is_running:
			for trace in self.traces:
				trace.reference_pool = self.reference_pool
				trace.iterations.clear()
				trace.metrics.clear()

			orchestrator.spawn(self.traces)
			self.pushButton.setIcon(QIcon(f"{util.RESOURCE}/stop"))
			self.pushButton.setText("00:00:00")
			self.elapsed_timer.second = 0
			self.elapsed_timer.start()
			self.polling_timer.start()
		else:
			self.polling_timer.stop()
			self.elapsed_timer.stop()
			self.pushButton.setIcon(QIcon(f"{util.RESOURCE}/start"))
			orchestrator.shutdown()


if __name__ == "__main__":
	app = QApplication(sys.argv)
	gui = Gui()
	gui.setFixedSize(gui.window().size())
	gui.show()
	sys.exit(app.exec())
