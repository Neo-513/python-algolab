from dataclasses import dataclass
from typing import Optional

import numpy as np
from skimage.metrics import structural_similarity as ssim

from . import pipeline


@dataclass(slots=True, kw_only=True)
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


def is_first_stage(stage):
	return stage <= INITIAL_STAGE


def should_advance_stage(stage, metric):
	if is_first_stage(stage):
		return True
	if metric >= STAGES[stage].advance_threshold:
		return True
	return False


def should_stop(stage):
	return stage >= FINAL_STAGE


def advance_stage(approximator):
	if not is_first_stage(approximator.stage):
		approximator.accepted.vertices *= 2

	approximator.stage += 1
	prop = approximator.proposal
	acc = approximator.accepted
	triangle_count = approximator.strategy.triangle_count
	resolution = STAGES[approximator.stage].resolution

	acc.texture = np.zeros((triangle_count, resolution, resolution, 3), dtype=np.float32)
	acc.mask = np.zeros((triangle_count, resolution, resolution, 1), dtype=np.float32)
	acc.invmask = np.zeros((triangle_count, resolution, resolution, 1), dtype=np.float32)
	acc.composite = np.zeros((triangle_count, resolution, resolution, 3), dtype=np.float32)
	approximator.composite_buffer = np.zeros((triangle_count, resolution, resolution, 3), dtype=np.float32)
	prop.patch = np.zeros((resolution, resolution, 4), dtype=np.uint8)

	for i in range(triangle_count):
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
	acc.metric = ssim(acc.approximation, approximator.reference_pool[STAGES[approximator.stage].resolution], channel_axis=2)
