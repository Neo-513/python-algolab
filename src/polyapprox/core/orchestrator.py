import multiprocessing

import numpy as np
import time

from . import config, stage,visual
from .approximator import Approximator

_processes: list[multiprocessing.Process] = []


def spawn(traces):
	_processes.clear()
	for trace in traces:
		args = trace.queue, trace.polygon_count, trace.vertex_count, trace.reference_pool
		process = multiprocessing.Process(target=_run, args=args)
		_processes.append(process)
		process.start()


def collect(traces):
	for trace in traces:
		while not trace.queue.empty():
			visual.refresh(trace)


def shutdown():
	for process in _processes:
		if process.is_alive():
			process.terminate()
	_processes.clear()


def _run(queue, polygon_count, vertex_count, reference_pool):
	approximator = Approximator(polygon_count, vertex_count, reference_pool)
	layers = np.random.randint(polygon_count, size=config.MAX_ITERATION, dtype=np.uint8)
	probs = np.random.randint(2, size=config.MAX_ITERATION, dtype=np.uint8)

	prop = approximator.proposal
	acc = approximator.accepted

	for iteration in range(config.MAX_ITERATION):
		if stage.should_stop(approximator):
			break

		approximation_data = None
		if stage.should_advance(approximator):
			stage.advance(approximator)
			approximation_data = acc.approximation.tobytes()
		else:
			prop.layer = layers[iteration]
			stage.update_perturbation(approximator)
			approximator.propose(probs[iteration])
			if prop.metric > acc.metric:
				approximator.accept()
				approximation_data = prop.approximation.tobytes()
		queue.put((iteration, acc.metric, acc.resolution, approximation_data))
		time.sleep(0.001)
