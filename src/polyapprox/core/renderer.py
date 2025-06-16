from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap

from . import config


def render_img(img_data, resolution):
	img = QImage(img_data, resolution, resolution, resolution * 3, QImage.Format.Format_RGB888)
	if resolution != config.FINAL_RESOLUTION:
		img = img.scaled(config.FINAL_RESOLUTION, config.FINAL_RESOLUTION, transformMode=Qt.TransformationMode.FastTransformation)
	return img


def render_reference(canvas, references, resolution=config.FINAL_RESOLUTION):
	img = render_img(references[resolution].data, resolution)
	canvas.setPixmap(QPixmap(img))


def render_approximation(canvas, approximation_data, resolution):
	img = render_img(approximation_data, resolution)
	canvas.setPixmap(QPixmap(img))
