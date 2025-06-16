from PyQt6.QtCore import QSize, QTimer, Qt
from PyQt6.QtGui import QImage, QIcon, QPixmap
from PyQt6.QtWidgets import QLabel, QMessageBox, QToolButton
import json
import os
import pickle
import sys

RESOURCE = os.path.join(getattr(sys, "_MEIPASS", ""), "resource").replace("\\", "/")


def cast(obj):
	return obj


def buttonize(push_button, func, icon, tip=None, ico_size=None):
	push_button.setIcon(QIcon(icon))
	push_button.setToolTip(tip) if tip else None
	push_button.setIconSize(QSize(ico_size, ico_size)) if ico_size is not None else None
	push_button.setStyleSheet("border: none") if isinstance(push_button, QToolButton) else None
	push_button.setCursor(Qt.CursorShape.PointingHandCursor)
	cast(push_button).clicked.connect(func)


def prompt(msg, icon):
	message_box = QMessageBox()
	message_box.setText(msg)
	message_box.setWindowIcon(QIcon(icon))
	message_box.setWindowTitle(" ")
	if icon.endswith("warning"):
		message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
	return message_box.exec() == QMessageBox.StandardButton.Yes


def fill(label, color=Qt.GlobalColor.transparent, create=False):
	pixmap = QPixmap(label.minimumSize()) if create else label.pixmap()
	pixmap.fill(color)
	label.setPixmap(pixmap)
	return pixmap


def elapsed(widget):
	def tick():
		timer.second += 1
		h, m, s = timer.second // 3600, (timer.second // 60) % 60, timer.second % 60
		widget.setText(f"{h:02}:{m:02}:{s:02}")

	timer = QTimer()
	timer.setInterval(1000)
	timer.second = 0
	cast(timer).timeout.connect(tick)
	return timer


def read(file_path):
	file_type = os.path.splitext(file_path)[-1]
	if file_type == ".pkl":
		with open(file_path, mode="rb") as file:
			datas = pickle.load(file)
	elif file_type == ".json":
		with open(file_path, mode="r", encoding="utf-8") as file:
			datas = json.load(file)
	else:
		with open(file_path, mode="r", encoding="utf-8") as file:
			datas = file.read()
	print(f"[READ] {file_path}")
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
	print(f"[WRITE] {file_path}")














def qtimer(interval, func):
	tmr = QTimer()
	tmr.setInterval(interval)
	cast(tmr).timeout.connect(func)
	tmr.second = 0
	return tmr


def mask(face, path=None, color=Qt.GlobalColor.transparent, hide=False, pointer=False):
	label = QLabel(parent=face.parent())
	label.setFixedSize(face.minimumSize())
	label.setGeometry(*cast(label.parent()).layout().getContentsMargins()[:2], label.width(), label.height())
	label.setHidden(hide)
	label.setCursor(Qt.CursorShape.PointingHandCursor) if pointer else None
	label.setPixmap(QPixmap(QImage(path))) if path is not None else None
	fill(label, color) if path is None else None
	return label
