from dataclasses import dataclass
from typing import Optional

import numpy as np
from skimage.metrics import structural_similarity as ssim

from . import pipeline


@dataclass(slots=True, kw_only=True, frozen=True)
class Stage:
	resolution: Optional[int] = None
	blur_kernel_size: Optional[int] = None
	advance_threshold: Optional[float] = None


STAGES = [
	Stage(resolution=16, blur_kernel_size=5, advance_threshold=0.8),
	Stage(resolution=32, blur_kernel_size=3, advance_threshold=0.75),
	Stage(resolution=64, blur_kernel_size=1, advance_threshold=0.65),
	Stage(resolution=128, blur_kernel_size=1, advance_threshold=0.8)
]

INITIAL_STAGE = - 1
FINAL_STAGE = len(STAGES)

INITIAL_RESOLUTION = STAGES[0].resolution
FINAL_RESOLUTION = STAGES[-1].resolution


class Phase:
	def __init__(self, approximator):
		self.approximator = approximator
		self.stage = INITIAL_STAGE

	def is_first_stage(self):
		return self.stage <= INITIAL_STAGE

	def should_advance(self):
		if self.is_first_stage():
			return True
		if self.approximator.accepted.metric >= STAGES[self.stage].advance_threshold:
			return True
		return False

	def should_stop(self):
		return self.stage >= FINAL_STAGE

	def advance(self):
		if self.is_first_stage():
			self.approximator.accepted.vertices = np.random.randint(
				INITIAL_RESOLUTION,
				size=(self.approximator.strategy.polygon_count, self.approximator.strategy.vertex_count * 2),
				dtype=np.int32
			)
		else:
			self.approximator.accepted.vertices *= 2

		self.stage += 1
		prop = self.approximator.proposal
		acc = self.approximator.accepted
		polygon_count = self.approximator.strategy.polygon_count
		resolution = STAGES[self.stage].resolution

		acc.texture = np.zeros((polygon_count, resolution, resolution, 3), dtype=np.float32)
		acc.mask = np.zeros((polygon_count, resolution, resolution, 1), dtype=np.float32)
		acc.invmask = np.zeros((polygon_count, resolution, resolution, 1), dtype=np.float32)
		acc.composite = np.zeros((polygon_count, resolution, resolution, 3), dtype=np.float32)
		self.approximator.composite_buffer = np.zeros((polygon_count, resolution, resolution, 3), dtype=np.float32)
		prop.patch = np.zeros((resolution, resolution, 4), dtype=np.uint8)

		for i in range(polygon_count):
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
		acc.metric = ssim(acc.approximation, self.approximator.reference_pool[STAGES[self.stage].resolution], channel_axis=2)

	def update_perturbation(self):
		res = STAGES[self.stage].resolution
		met = self.approximator.accepted.metric
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
			self.approximator.perturbation = pert


# PERTURB_SCHEDULE = {
#     128: {
#         0.56: (4, 10),
#         0.6: (8, 8),
#         0.66: (1, 7),
#         0.74: (1, 1),
#     },
#     64: {
#         0.6: (4, 15),
#     },
# }