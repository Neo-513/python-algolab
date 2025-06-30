import cv2
import numpy as np


def rasterize(proposal):
	proposal.patch.fill(0)
	cv2.fillPoly(proposal.patch, [proposal.vertices.reshape(-1, 2)], proposal.color.tolist())
	proposal.texture = proposal.patch[..., :3].copy()
	proposal.mask = proposal.patch[..., 3:].copy() / 255
	proposal.invmask = 1 - proposal.mask


def disturb(proposal, prob, perturb, resolution):
	if prob >= 0.5:
		noise = np.random.randint(-perturb.vertices, perturb.vertices + 1, size=proposal.vertices.shape[0])
		proposal.vertices = proposal.vertices + noise
		np.clip(proposal.vertices, 0, resolution - 1, out=proposal.vertices)
	else:
		noise = np.random.randint(-perturb.color, perturb.color + 1, size=proposal.color.shape[0])
		proposal.color = proposal.color + noise
		np.clip(proposal.color, 0, 255, out=proposal.color)


def blend(proposal, accepted, composites):
	base = 0 if proposal.layer == 0 else accepted.composite[proposal.layer - 1]
	composites[proposal.layer] = proposal.mask * proposal.texture + proposal.invmask * base
	for i in range(proposal.layer + 1, composites.shape[0]):
		composites[i] = accepted.mask[i] * accepted.texture[i] + accepted.invmask[i] * composites[i - 1]
