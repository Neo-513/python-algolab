import numpy as np
from skimage.metrics import structural_similarity as ssim

from . import config, pipeline


def is_first_stage(approximator):
	return approximator.accepted.resolution not in config.SUPPORTED_RESOLUTIONS


def should_advance(approximator):
	if is_first_stage(approximator):
		return True
	acc = approximator.accepted
	if acc.resolution != config.FINAL_RESOLUTION and acc.metric >= config.STAGE_THRESHOLDS[acc.resolution]:
		return True
	return False


def should_stop(approximator):
	acc = approximator.accepted
	return acc.resolution == config.FINAL_RESOLUTION and acc.metric >= config.STAGE_THRESHOLDS[acc.resolution]


def advance(approximator):
	should_build = is_first_stage(approximator)
	_advance_resolution(approximator, should_build)
	_advance_vertices(approximator, should_build)
	_advance_stage(approximator)


def _advance_resolution(approximator, should_build):
	if should_build:
		approximator.accepted.resolution = config.INITIAL_RESOLUTION
	else:
		approximator.accepted.resolution *= 2


def _advance_vertices(approximator, should_build):
	if should_build:
		approximator.accepted.vertices = np.random.randint(config.INITIAL_RESOLUTION, size=(approximator.polygon_count, approximator.vertex_count * 2), dtype=np.int32)
	else:
		approximator.accepted.vertices *= 2


def _advance_stage(approximator):
	prop = approximator.proposal
	acc = approximator.accepted

	acc.texture = np.zeros((approximator.polygon_count, acc.resolution, acc.resolution, 3), dtype=np.float32)
	acc.mask = np.zeros((approximator.polygon_count, acc.resolution, acc.resolution, 1), dtype=np.float32)
	acc.invmask = np.zeros((approximator.polygon_count, acc.resolution, acc.resolution, 1), dtype=np.float32)
	acc.composite = np.zeros((approximator.polygon_count, acc.resolution, acc.resolution, 3), dtype=np.float32)
	approximator.buffer.composite = acc.composite.copy()
	prop.patch = np.zeros((acc.resolution, acc.resolution, 4), dtype=np.uint8)

	for i in range(approximator.polygon_count):
		prop.vertices = acc.vertices[i]
		prop.color = acc.color[i]
		pipeline.rasterize(prop)
		acc.texture[i] = prop.texture
		acc.mask[i] = prop.mask
		acc.invmask[i] = prop.invmask

	prop.texture = acc.texture[0]
	prop.mask = acc.mask[0]
	prop.invmask = acc.invmask[0]

	prop.layer = 0
	pipeline.blend(prop, acc, acc.composite)
	acc.approximation = np.clip(acc.composite[-1], 0, 255).astype(np.uint8)
	acc.metric = min(max(ssim(approximator.references[acc.resolution], acc.approximation, channel_axis=2), 0), 1)


def update_perturbation(approximator):
	res = approximator.accepted.resolution
	met = approximator.accepted.metric
	pert = None

	if res == 16:
		pert = 10, 30
	if res == 32:
		pert = 8, 25

	if res == 64:
		pert = 6, 20
	if res == 64 and met >= 0.6:
		pert = 4, 15

	if res == 128 and met:
		pert = 4, 10
	if res == 128 and met >= 0.56:
		pert = 4, 9
	if res == 128 and met >= 0.58:
		pert = 8, 8
	if res == 128 and met >= 0.6:
		pert = 8, 8
	if res == 128 and met >= 0.66:
		pert = 1, 7
	if res == 128 and met >= 0.68:
		pert = 1, 6
	if res == 128 and met >= 0.7:
		pert = 1, 5
	if res == 128 and met >= 0.71:
		pert = 1, 4
	if res == 128 and met >= 0.72:
		pert = 1, 3
	if res == 128 and met >= 0.73:
		pert = 1, 2
	if res == 128 and met >= 0.74:
		pert = 1, 1

	if pert is not None:
		approximator.perturbation = pert
