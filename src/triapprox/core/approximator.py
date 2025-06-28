from dataclasses import dataclass
from typing import Optional

import numpy as np
from skimage.metrics import structural_similarity as ssim

from . import pipeline
from .advancer import INITIAL_RESOLUTION, INITIAL_STAGE, STAGES





@dataclass(slots=True, kw_only=True)
class Proposal:
	layer: Optional[int] = None
	patch: Optional[np.ndarray] = None
	vertices: Optional[np.ndarray] = None
	color: Optional[np.ndarray] = None
	texture: Optional[np.ndarray] = None
	mask: Optional[np.ndarray] = None
	invmask: Optional[np.ndarray] = None
	approximation: Optional[np.ndarray] = None
	metric: Optional[float] = None


@dataclass(slots=True, kw_only=True)
class Accepted:
	vertices: Optional[np.ndarray] = None
	color: Optional[np.ndarray] = None
	texture: Optional[np.ndarray] = None
	mask: Optional[np.ndarray] = None
	invmask: Optional[np.ndarray] = None
	composite: Optional[np.ndarray] = None
	approximation: Optional[np.ndarray] = None
	metric: Optional[float] = None


class Approximator:
	def __init__(self, strategy, reference_pool):
		self.strategy = strategy
		self.reference_pool = reference_pool
		self.composite_buffer = None

		self.proposal = Proposal()
		self.accepted = Accepted(
			vertices=np.random.randint(INITIAL_RESOLUTION, size=(self.strategy.triangle_count, 6), dtype=np.int32),
			color=np.random.randint(256, size=(self.strategy.triangle_count, 4), dtype=np.int32)
		)

		self.perturbation = (0, 0)
		self.stage = INITIAL_STAGE

	def propose(self, prob):
		self.proposal.vertices = self.accepted.vertices[self.proposal.layer]
		self.proposal.color = self.accepted.color[self.proposal.layer]
		pipeline.perturb(self.proposal, prob, self.perturbation, STAGES[self.stage].resolution)
		pipeline.rasterize(self.proposal)
		pipeline.blend(self.proposal, self.accepted, self.composite_buffer)
		self.proposal.approximation = np.clip(self.composite_buffer[-1], 0, 255).astype(np.uint8)
		self.proposal.metric = ssim(self.proposal.approximation, self.reference_pool[STAGES[self.stage].resolution], channel_axis=2)

	def accept(self):
		self.accepted.vertices[self.proposal.layer] = self.proposal.vertices
		self.accepted.color[self.proposal.layer] = self.proposal.color
		self.accepted.texture[self.proposal.layer] = self.proposal.texture
		self.accepted.mask[self.proposal.layer] = self.proposal.mask
		self.accepted.invmask[self.proposal.layer] = self.proposal.invmask
		self.accepted.composite[self.proposal.layer:] = self.composite_buffer[self.proposal.layer:]
		self.accepted.metric = self.proposal.metric

	def update_perturbation(self):
		res = STAGES[self.stage].resolution
		met = self.accepted.metric
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
			self.perturbation = pert


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