import cv2
import numpy as np

CHANNEL_RGBA_TO_BGRA = [2, 1, 0, 3]


def rasterize(proposal):
	proposal.patch.fill(0)
	cv2.fillPoly(proposal.patch, [proposal.vertices.reshape(-1, 2)], proposal.color[CHANNEL_RGBA_TO_BGRA].tolist())
	proposal.texture = proposal.patch[..., :3].copy()
	proposal.mask = proposal.patch[..., 3:].copy() / 255
	proposal.invmask = 1 - proposal.mask


def perturb(proposal, prob, perturbation, vert_bounds, color_bounds=(0, 255)):
	if prob:
		proposal.vertices = proposal.vertices + np.random.randint(-perturbation[0], perturbation[0] + 1, size=proposal.vertices.shape[0])
	else:
		proposal.color = proposal.color + np.random.randint(-perturbation[1], perturbation[1] + 1, size=proposal.color.shape[0])
	np.clip(proposal.vertices, *vert_bounds, out=proposal.vertices)
	np.clip(proposal.color, *color_bounds, out=proposal.color)


def blend(proposal, accepted, composites):
	backdrop = 0 if proposal.layer == 0 else accepted.composite[proposal.layer - 1]
	composites[proposal.layer] = proposal.mask * proposal.texture + proposal.invmask * backdrop
	for i in range(proposal.layer + 1, composites.shape[0]):
		composites[i] = accepted.mask[i] * accepted.texture[i] + accepted.invmask[i] * composites[i - 1]
