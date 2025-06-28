import time
from dataclasses import dataclass
from multiprocessing import Process
from queue import Empty
from typing import Optional

import numpy as np

from . import advancer
from .approximator import Approximator


@dataclass(slots=True, kw_only=True)
class Strategy:
	triangle_count: Optional[int] = None


@dataclass(slots=True, kw_only=True)
class Snapshot:
	iteration: Optional[int] = None
	stage: Optional[int] = None
	metric: Optional[float] = None
	approximation: Optional[bytes] = None


MAX_ITERATION = 100000 * 3
STRATEGIES = [
	Strategy(triangle_count=50),
	Strategy(triangle_count=50),
	Strategy(triangle_count=50)
]


class Runner:
	def __init__(self, visualizer):
		self.visualizer = visualizer
		self.processes = []

	def spawn(self):
		self.processes.clear()
		for i, trace in enumerate(self.visualizer.traces):
			args = trace.queue, STRATEGIES[i], self.visualizer.reference_pool
			process = Process(target=optimize, args=args)
			self.processes.append(process)
			process.start()

	def poll(self):
		for trace in self.visualizer.traces:
			snapshot = None
			while True:
				try:
					snapshot = trace.queue.get_nowait()
				except Empty:
					break
			if snapshot:
				self.visualizer.refresh(trace, snapshot)

	def shutdown(self):
		for process in self.processes:
			if process.is_alive():
				process.terminate()
				process.join()
		self.processes.clear()


def optimize(queue, strategy, reference_pool):
	approximator = Approximator(strategy, reference_pool)
	layers = np.random.randint(strategy.triangle_count, size=MAX_ITERATION, dtype=np.uint8)
	probs = np.random.randint(2, size=MAX_ITERATION, dtype=np.uint8)

	for iteration in range(MAX_ITERATION):
		if advancer.should_stop(approximator.stage):
			break
		if advancer.should_advance_stage(approximator.stage, approximator.accepted.metric):
			_advance(queue, approximator, iteration)
		else:
			_step(queue, approximator, iteration, layers[iteration], probs[iteration])
		time.sleep(0.001)


def _advance(queue, approximator, iteration):
	advancer.advance_stage(approximator)
	queue.put(Snapshot(
		iteration=iteration,
		stage=approximator.stage,
		metric=approximator.accepted.metric,
		approximation=approximator.accepted.approximation.tobytes()
	))


def _step(queue, approximator, iteration, layer, prob):
	data = None
	approximator.proposal.layer = layer
	approximator.update_perturbation()
	approximator.propose(prob)

	if approximator.proposal.metric > approximator.accepted.metric:
		approximator.accept()
		data = approximator.proposal.approximation.tobytes()

	queue.put(Snapshot(
		iteration=iteration,
		stage=approximator.stage,
		metric=approximator.accepted.metric,
		approximation=data
	))
