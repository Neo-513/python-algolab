import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow
from shared import util

from core import loader
from core.runner import Runner
from core.visualizer import Visualizer
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
		util.fill(self.label_reference, create=True)
		util.fill(self.label_approximation0, create=True)
		util.fill(self.label_approximation1, create=True)
		util.fill(self.label_approximation2, create=True)
		util.buttonize(self.pushButton, self.approximate, f"{util.RESOURCE}/start")

		self.visualizer = Visualizer(self.groupBox_plot, self)
		self.runner = Runner(self.visualizer)

		self.is_running = False
		self.elapsed_timer = util.elapsed(self.pushButton)
		self.polling_timer = util.qtimer(16, self.runner.collect)
		self.reference_pools = loader.load_reference_pools(loader.PRELOAD_REFERENCE_NAMES)
		self.radioButton_monalisa.click()

	def show_curve(self, state, trace_id):
		self.visualizer.traces[trace_id].tracer.chart_curve.setVisible(state)
		self.visualizer.traces[trace_id].tracer.chart_cursor.setVisible(state)

	def switch(self, reference_name):
		self.visualizer.reference_pool = None
		util.fill(self.label_reference)
		util.fill(self.label_approximation0)
		util.fill(self.label_approximation1)
		util.fill(self.label_approximation2)

		if reference_name == "custom":
			reference_path = QFileDialog.getOpenFileName(filter="*.png")[0]
			if not reference_path:
				return
			self.visualizer.reference_pool = loader.load_reference_pool(reference_path)
		else:
			self.visualizer.reference_pool = self.reference_pools[reference_name]
		self.visualizer.render(self.label_reference)

	def approximate(self):
		if not self.visualizer.reference_pool:
			return util.prompt("请选择图片", "error")

		self.is_running = not self.is_running
		self.radioButton_monalisa.setDisabled(self.is_running)
		self.radioButton_firefox.setDisabled(self.is_running)
		self.radioButton_darwin.setDisabled(self.is_running)
		self.radioButton_custom.setDisabled(self.is_running)

		if self.is_running:
			self.visualizer.clear()
			self.runner.spawn()
			self.pushButton.setIcon(QIcon(f"{util.RESOURCE}/stop"))
			self.pushButton.setText("00:00:00")
			self.elapsed_timer.second = 0
			self.elapsed_timer.start()
			self.polling_timer.start()
		else:
			self.polling_timer.stop()
			self.elapsed_timer.stop()
			self.pushButton.setIcon(QIcon(f"{util.RESOURCE}/start"))
			self.runner.shutdown()


if __name__ == "__main__":
	app = QApplication(sys.argv)
	gui = Gui()
	gui.setFixedSize(gui.window().size())
	gui.show()
	sys.exit(app.exec())
