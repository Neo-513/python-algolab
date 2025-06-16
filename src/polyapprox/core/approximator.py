import numpy as np
from skimage.metrics import structural_similarity as ssim

from . import pipeline
from .structures import Accepted, Buffer, Proposal


class Approximator:
	def __init__(self, polygon_count, vertex_count, references):
		self.polygon_count = polygon_count
		self.vertex_count = vertex_count
		self.references = references

		self.proposal = Proposal()
		self.accepted = Accepted(color=np.random.randint(256, size=(self.polygon_count, 4), dtype=np.int32))
		self.buffer = Buffer()

		self.perturbation = (0, 0)

	def propose(self, prob):
		self.proposal.vertices = self.accepted.vertices[self.proposal.layer]
		self.proposal.color = self.accepted.color[self.proposal.layer]
		pipeline.perturb(self.proposal, prob, self.perturbation, (0, self.accepted.resolution - 1))
		pipeline.rasterize(self.proposal)
		pipeline.blend(self.proposal, self.accepted, self.buffer.composite)
		self.proposal.approximation = np.clip(self.buffer.composite[-1], 0, 255).astype(np.uint8)
		self.proposal.metric = min(max(ssim(self.references[self.accepted.resolution], self.proposal.approximation, channel_axis=2), 0), 1)

	def accept(self):
		self.accepted.vertices[self.proposal.layer] = self.proposal.vertices
		self.accepted.color[self.proposal.layer] = self.proposal.color
		self.accepted.texture[self.proposal.layer] = self.proposal.texture
		self.accepted.mask[self.proposal.layer] = self.proposal.mask
		self.accepted.invmask[self.proposal.layer] = self.proposal.invmask
		self.accepted.composite[self.proposal.layer:] = self.buffer.composite[self.proposal.layer:]
		self.accepted.metric = self.proposal.metric
