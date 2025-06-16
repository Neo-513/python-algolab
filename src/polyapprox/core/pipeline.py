import cv2
import numpy as np

from . import config


def rasterize(proposal):
	proposal.patch.fill(0)
	cv2.fillPoly(proposal.patch, [proposal.vertices.reshape(-1, 2)], proposal.color[config.CHANNEL_RGBA_TO_BGRA].tolist())
	proposal.texture = proposal.patch[..., :3].copy()
	proposal.mask = proposal.patch[..., 3:].copy() / 255
	proposal.invmask = 1 - proposal.mask
	# proposal.texture = proposal.patch[..., :3].astype(np.float32)
	# proposal.mask = proposal.patch[..., 3:].astype(np.float32) / 255
	# proposal.invmask = (1 - proposal.mask).astype(np.float32)


def perturb(proposal, prob, perturbation, vert_bounds, color_bounds=(0, 255)):
	if prob:
		proposal.vertices = proposal.vertices + np.random.randint(-perturbation[0], perturbation[0] + 1, size=proposal.vertices.shape[0])
	else:
		proposal.color = proposal.color + np.random.randint(-perturbation[1], perturbation[1] + 1, size=proposal.color.shape[0])
	np.clip(proposal.vertices, *vert_bounds, out=proposal.vertices)
	np.clip(proposal.color, *color_bounds, out=proposal.color)


def blend(proposal, accepted, composites):
	composites[proposal.layer] = proposal.mask * proposal.texture + proposal.invmask * backdrop(proposal, accepted)
	for i in range(proposal.layer + 1, composites.shape[0]):
		composites[i] = accepted.mask[i] * accepted.texture[i] + accepted.invmask[i] * composites[i - 1]


def backdrop(proposal, accepted):
	if proposal.layer == 0:
		return config.BACKDROP[accepted.resolution]
	else:
		return accepted.composite[proposal.layer - 1]
