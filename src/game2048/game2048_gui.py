import sys

import numpy as np
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow
from shared import util

from core import bot, engine, renderer
from core.constants import C
from core.structures import Frame, Viewport
from ui.gui_ui import Ui_MainWindow


class Gui(QMainWindow, Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)

		self.setWindowIcon(QIcon(util.resource("logo.png")))
		util.buttonize(self.pushButton, self.reset, None)
		util.buttonize(self.toolButton, self.toggle_bot_mode, util.resource("bot_off.png"), ico_size=32)
		self.label.mousePressEvent = self.on_mouse_pressed
		self.label.mouseReleaseEvent = self.on_mouse_released

		self.current = engine.build()
		self.previous = np.zeros_like(self.current)

		self.viewport = Viewport(canvas=QPixmap(C.BoardStyle.BOARD_SIZE, C.BoardStyle.BOARD_SIZE), viewer=self.label)
		self.frame = Frame(previous=self.previous, current=self.current)

		self.animator = util.poller(C.Anim.FRAME_INTERVAL, self.animate_act)
		self.game_state = self.bot_active = self.mouse_pos = None
		self.reset()

	def reset(self):
		self.animator.stop()
		self.animator.timeout.disconnect(self.animate_act)
		self.animator.timeout.connect(self.animate_spawn)

		self.game_state = C.GameStatus.CONTINUE
		self.bot_active = False
		self.toolButton.setIcon(QIcon(util.resource("bot_off.png")))

		spawns = engine.initialize(self.current)
		renderer.render_static_frame(self.viewport)

		self.frame.tick = 0
		self.frame.spawns = spawns
		self.animator.start()

	def keyPressEvent(self, event):
		if not self.animator.isActive():
			if event.key() in C.Move.KEYS:
				self.act(C.Move.KEYS[event.key()])

	def on_mouse_pressed(self, event):
		if not self.animator.isActive():
			self.mouse_pos = event.pos()

	def on_mouse_released(self, event):
		if not self.animator.isActive():
			dx = event.pos().x() - self.mouse_pos.x()
			dy = event.pos().y() - self.mouse_pos.y()
			if abs(dx) >= abs(dy):
				movement = C.Move.RIGHT if dx >= 0 else C.Move.LEFT
			else:
				movement = C.Move.DOWN if dy >= 0 else C.Move.UP
			self.act(movement)

	def toggle_bot_mode(self):
		if self.bot_active:
			self.bot_active = False
			self.toolButton.setIcon(QIcon(util.resource("bot_off.png")))
		else:
			self.bot_active = True
			self.toolButton.setIcon(QIcon(util.resource("bot_on.png")))
			self.act(bot.decide(self.current))

	def act(self, movement):
		self.previous[:] = self.current
		engine.move(self.current, movement)

		spawns = []
		if self.game_state == C.GameStatus.CONTINUE and engine.is_win(self.current):
			self.game_state = C.GameStatus.WIN
		if engine.should_spawn(self.previous, self.current):
			spawns.append(engine.spawn(self.current))
		if self.game_state == C.GameStatus.CONTINUE and engine.is_lose(self.current):
			self.game_state = C.GameStatus.LOSE

		self.frame.tick = 0
		self.frame.slide_tick = 0
		self.frame.emerge_tick = 0
		self.frame.movement = movement
		self.frame.spawns = spawns
		self.animator.start()

	def animate_spawn(self):
		if self.frame.tick < C.Anim.FRAME_COUNT:
			renderer.render_spawn_frame(self.viewport, self.frame)
			self.frame.tick += 1
		else:
			self.animator.stop()
			self.animator.timeout.disconnect(self.animate_spawn)
			self.animator.timeout.connect(self.animate_act)

	def animate_act(self):
		if self.frame.slide_tick < C.Anim.FRAME_COUNT:
			self.frame.tick = self.frame.slide_tick
			renderer.render_static_frame(self.viewport)
			renderer.render_slide_frame(self.viewport, self.frame)
			self.frame.slide_tick += 1
		elif self.frame.emerge_tick < C.Anim.FRAME_COUNT:
			self.frame.tick = self.frame.emerge_tick
			renderer.render_spawn_frame(self.viewport, self.frame)
			renderer.render_merge_frame(self.viewport, self.frame)
			self.frame.emerge_tick += 1
		else:
			self.animator.stop()
			if self.game_state == C.GameStatus.WIN:
				self.toolButton.setIcon(QIcon(util.resource("bot_off.png")))
				util.popup("You win", util.resource("success.png"))
				self.reset()
				return
			if self.game_state == C.GameStatus.LOSE:
				self.toolButton.setIcon(QIcon(util.resource("bot_off.png")))
				util.popup("You lose", util.resource("error.png"))
				self.reset()
				return
			if self.bot_active:
				self.act(bot.decide(self.current))


if __name__ == "__main__":
	app = QApplication(sys.argv)
	gui = Gui()
	gui.setFixedSize(gui.window().size())
	gui.show()
	sys.exit(app.exec())
