import time
from collections import deque
from dataclasses import dataclass
from multiprocessing import Process
from queue import Empty
from typing import Optional

import numpy as np

from .approximator import Approximator
from .phase import STAGES


@dataclass(slots=True, kw_only=True, frozen=True)
class Strategy:
	polygon_count: Optional[int] = None
	vertex_count: Optional[int] = None

STRATEGIES = [
	Strategy(polygon_count=50, vertex_count=3),
	Strategy(polygon_count=50, vertex_count=3),
	Strategy(polygon_count=50, vertex_count=3)
]
MAX_ITERATION = 100000 * 3


class Runner:
	def __init__(self, visualizer):
		self.visualizer = visualizer
		self.processes = []

	def spawn(self):
		self.processes.clear()
		for i, trace in enumerate(self.visualizer.traces):
			args = trace.queue, STRATEGIES[i], self.visualizer.reference_pool
			process = Process(target=self._run, args=args)
			self.processes.append(process)
			process.start()

	def collect(self):
		for trace in self.visualizer.traces:
			dq = deque(maxlen=1)
			while True:
				try:
					dq.append(trace.queue.get_nowait())
				except Empty:
					break

			if dq:
				iteration, metric, resolution, data = dq[0]
				# 只渲染最新一次状态
				self.visualizer.refresh(trace, iteration, metric, resolution, data)

			# while not trace.queue.empty():
				# 	self.visualizer.refresh(trace)

	def shutdown(self):
		for process in self.processes:
			if process.is_alive():
				process.terminate()
				process.join()
		self.processes.clear()

	@staticmethod
	def _run(queue, strategy, reference_pool):
		approximator = Approximator(strategy, reference_pool)
		layers = np.random.randint(strategy.polygon_count, size=MAX_ITERATION, dtype=np.uint8)
		probs = np.random.randint(2, size=MAX_ITERATION, dtype=np.uint8)

		prop = approximator.proposal
		acc = approximator.accepted

		for iteration in range(MAX_ITERATION):
			if approximator.phase.should_stop():
				break

			data = None
			if approximator.phase.should_advance():
				approximator.phase.advance()
				data = acc.approximation.tobytes()
			else:
				prop.layer = layers[iteration]
				approximator.phase.update_perturbation()
				approximator.propose(probs[iteration])
				if prop.metric > acc.metric:
					approximator.accept()
					data = prop.approximation.tobytes()
			queue.put((iteration, acc.metric, STAGES[approximator.phase.stage].resolution, data))
			time.sleep(0.001)
