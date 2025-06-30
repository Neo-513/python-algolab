from collections import deque

import numpy as np
from skimage.metrics import structural_similarity as ssim

from . import constants, pipeline
from .structures import Opt


class Approximator:
	def __init__(self, ref_pool):
		self.ref_pool = ref_pool
		self.perturb = constants.INITIAL_PERTURB
		self.composite_buffer = None

		self.stages = deque(stage for stage in constants.STAGES)
		self.stage = None

		self.proposal = Opt.Proposal()
		self.accepted = Opt.Accepted(
			vertices=np.random.randint(constants.INITIAL_RESOLUTION, size=(constants.TRIANGLE_COUNT, 6), dtype=np.int32),
			color=np.random.randint(256, size=(constants.TRIANGLE_COUNT, 4), dtype=np.int32)
		)

	def propose(self, prob):
		self.proposal.vertices = self.accepted.vertices[self.proposal.layer]
		self.proposal.color = self.accepted.color[self.proposal.layer]
		pipeline.disturb(self.proposal, prob, self.perturb, self.stage.resolution)
		pipeline.rasterize(self.proposal)
		pipeline.blend(self.proposal, self.accepted, self.composite_buffer)
		self.proposal.approx = np.clip(self.composite_buffer[-1], 0, 255).astype(np.uint8)
		self.proposal.metric = ssim(self.proposal.approx, self.ref_pool[self.stage.resolution], channel_axis=2)

	def accept(self):
		self.accepted.vertices[self.proposal.layer] = self.proposal.vertices
		self.accepted.color[self.proposal.layer] = self.proposal.color
		self.accepted.texture[self.proposal.layer] = self.proposal.texture
		self.accepted.mask[self.proposal.layer] = self.proposal.mask
		self.accepted.invmask[self.proposal.layer] = self.proposal.invmask
		self.accepted.composite[self.proposal.layer:] = self.composite_buffer[self.proposal.layer:]
		self.accepted.approx = self.proposal.approx
		self.accepted.metric = self.proposal.metric

	def advance(self):
		if self.stage is not None:
			self.accepted.vertices *= 2
		self.stage = self.stages.popleft()

		resolution = self.stage.resolution
		self.accepted.texture = np.zeros((constants.TRIANGLE_COUNT, resolution, resolution, 3), dtype=np.float32)
		self.accepted.mask = np.zeros((constants.TRIANGLE_COUNT, resolution, resolution, 1), dtype=np.float32)
		self.accepted.invmask = np.zeros((constants.TRIANGLE_COUNT, resolution, resolution, 1), dtype=np.float32)
		self.accepted.composite = np.zeros((constants.TRIANGLE_COUNT, resolution, resolution, 3), dtype=np.float32)
		self.composite_buffer = np.zeros((constants.TRIANGLE_COUNT, resolution, resolution, 3), dtype=np.float32)
		self.proposal.patch = np.zeros((resolution, resolution, 4), dtype=np.uint8)

		for i in range(constants.TRIANGLE_COUNT):
			self.proposal.vertices = self.accepted.vertices[i]
			self.proposal.color = self.accepted.color[i]
			pipeline.rasterize(self.proposal)
			self.accepted.texture[i] = self.proposal.texture
			self.accepted.mask[i] = self.proposal.mask
			self.accepted.invmask[i] = self.proposal.invmask

		self.proposal.layer = 0
		self.proposal.texture = self.accepted.texture[self.proposal.layer]
		self.proposal.mask = self.accepted.mask[self.proposal.layer]
		self.proposal.invmask = self.accepted.invmask[self.proposal.layer]
		pipeline.blend(self.proposal, self.accepted, self.accepted.composite)
		self.accepted.approx = np.clip(self.accepted.composite[-1], 0, 255).astype(np.uint8)
		self.accepted.metric = ssim(self.accepted.approx, self.ref_pool[self.stage.resolution], channel_axis=2)

	def resolve(self):
		for strategy in constants.STRATEGIES[self.stage.resolution]:
			if self.accepted.metric >= strategy.threshold:
				self.perturb.vertices = strategy.perturb.vertices
				self.perturb.color = strategy.perturb.color
				return
