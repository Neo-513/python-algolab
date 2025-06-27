from dataclasses import dataclass
from typing import Optional

import numpy as np
from skimage.metrics import structural_similarity as ssim

from . import pipeline
from .phase import STAGES, Phase


class Approximator:
	@dataclass(slots=True, kw_only=True)
	class _Proposal:
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
	class _Accepted:
		vertices: Optional[np.ndarray] = None
		color: Optional[np.ndarray] = None
		texture: Optional[np.ndarray] = None
		mask: Optional[np.ndarray] = None
		invmask: Optional[np.ndarray] = None
		composite: Optional[np.ndarray] = None
		approximation: Optional[np.ndarray] = None
		metric: Optional[float] = None

	def __init__(self, strategy, reference_pool):
		self.strategy = strategy
		self.reference_pool = reference_pool
		self.composite_buffer = None

		self.phase = Phase(self)
		self.proposal = self._Proposal()
		self.accepted = self._Accepted(color=np.random.randint(256, size=(self.strategy.polygon_count, 4), dtype=np.int32))

		self.perturbation = (0, 0)

	def propose(self, prob):
		self.proposal.vertices = self.accepted.vertices[self.proposal.layer]
		self.proposal.color = self.accepted.color[self.proposal.layer]
		pipeline.perturb(self.proposal, prob, self.perturbation, (0, STAGES[self.phase.stage].resolution - 1))
		pipeline.rasterize(self.proposal)
		pipeline.blend(self.proposal, self.accepted, self.composite_buffer)
		self.proposal.approximation = np.clip(self.composite_buffer[-1], 0, 255).astype(np.uint8)
		self.proposal.metric = ssim(self.proposal.approximation, self.reference_pool[STAGES[self.phase.stage].resolution], channel_axis=2)

	def accept(self):
		self.accepted.vertices[self.proposal.layer] = self.proposal.vertices
		self.accepted.color[self.proposal.layer] = self.proposal.color
		self.accepted.texture[self.proposal.layer] = self.proposal.texture
		self.accepted.mask[self.proposal.layer] = self.proposal.mask
		self.accepted.invmask[self.proposal.layer] = self.proposal.invmask
		self.accepted.composite[self.proposal.layer:] = self.composite_buffer[self.proposal.layer:]
		self.accepted.metric = self.proposal.metric
