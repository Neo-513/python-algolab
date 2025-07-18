import json
import os
import pickle
import sys
from functools import wraps

from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox, QToolButton


def cast(obj):
	return obj


def resource(res):
	return os.path.join(getattr(sys, "_MEIPASS", ""), "resource").replace("\\", "/") + "/" + res


def buttonize(push_button, func, icon, tip=None, ico_size=None):
	push_button.setIcon(QIcon(icon))
	push_button.setToolTip(tip) if tip else None
	push_button.setIconSize(QSize(ico_size, ico_size)) if ico_size is not None else None
	push_button.setStyleSheet("border: none") if isinstance(push_button, QToolButton) else None
	push_button.setCursor(Qt.CursorShape.PointingHandCursor)
	cast(push_button).clicked.connect(func)


def popup(msg, icon):
	message_box = QMessageBox()
	message_box.setText(msg)
	message_box.setWindowIcon(QIcon(icon))
	message_box.setWindowTitle(" ")
	if "warning" in icon:
		message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
	return message_box.exec() == QMessageBox.StandardButton.Yes


def poller(interval, func):
	timer = QTimer()
	timer.setInterval(interval)
	cast(timer).timeout.connect(func)
	return timer


def ticker(push_button):
	def tick():
		timer.second += 1
		h, m, s = timer.second // 3600, (timer.second // 60) % 60, timer.second % 60
		push_button.setText(f"{h:02}:{m:02}:{s:02}")

	timer = poller(1000, tick)
	timer.second = 0
	return timer


def read(file_path):
	file_type = os.path.splitext(file_path)[-1]
	if file_type == ".pkl":
		with open(file_path, mode="rb") as file:
			datas = pickle.load(file)
	elif file_type == ".json":
		with open(file_path, encoding="utf-8") as file:
			datas = json.load(file)
	else:
		with open(file_path, encoding="utf-8") as file:
			datas = file.read()
	return datas


def write(file_path, datas):
	file_type = os.path.splitext(file_path)[-1]
	if file_type == ".pkl":
		with open(file_path, mode="wb") as file:
			pickle.dump(datas, cast(file))
	elif file_type == ".json":
		with open(file_path, mode="w", encoding="utf-8") as file:
			json.dump(datas, cast(file))
	else:
		with open(file_path, mode="w", encoding="utf-8") as file:
			file.write(datas)


def graphic(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		app = QApplication([])
		try:
			result = func(*args, **kwargs)
			return result
		finally:
			app.quit()
	return wrapper
