import time

import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from shared import util

from . import constants
from .approximator import Approximator
from .structures import Opt


class Worker(QThread):
	snapshot_ready = pyqtSignal(Opt.Snapshot)

	def __init__(self, ref_pool):
		super().__init__()
		self.is_running = False
		self.approximator = Approximator(ref_pool)

		self.layers = np.random.randint(constants.TRIANGLE_COUNT, size=constants.MAX_ITERATION, dtype=np.uint8)
		self.probs = np.random.random(size=constants.MAX_ITERATION)
		self.last_emit_time = time.time()

	def run(self):
		self.is_running = True
		for iteration in range(constants.MAX_ITERATION):
			if not self.is_running:# or not approximator.stages:
				break

			if self.approximator.stage is None or self.approximator.accepted.metric >= self.approximator.stage.advance_threshold:
				self.approximator.advance()
			else:
				self.approximator.proposal.layer = self.layers[iteration]
				self.approximator.resolve()
				self.approximator.propose(self.probs[iteration])
				self.approximator.step_greedy()
				# if approximator.stage.resolution == constants.FINAL_RESOLUTION and approximator.accepted.metric >= 0.62:
				# 	self.approximator.step_sa(iteration)
				# else:
				# 	self.approximator.step_greedy()

			now = time.time()
			if now - self.last_emit_time >= 0.015:
				self.last_emit_time = now

				util.cast(self.snapshot_ready).emit(Opt.Snapshot(
					iteration=iteration,
					stage=self.approximator.stage,
					approx=self.approximator.accepted.approx.tobytes(),
					metric=self.approximator.accepted.metric
				))

	def shutdown(self):
		self.is_running = False
		self.quit()
		self.wait()
