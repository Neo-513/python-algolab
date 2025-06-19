import cv2
import numpy as np
from shared import util

from . import phase

PRELOAD_REFERENCE_NAMES = ("mona_lisa", "firefox", "darwin")


def load_reference_pool(reference_path, dtype=np.uint8):
	reference = cv2.cvtColor(cv2.imread(reference_path), cv2.COLOR_BGR2RGB)
	reference_pool = {}
	for stage in phase.STAGES:
		resized_reference = cv2.resize(reference, (stage.resolution, stage.resolution))
		blurred_reference = cv2.GaussianBlur(resized_reference, (stage.blur_kernel_size, stage.blur_kernel_size), 0)
		reference_pool[stage.resolution] = blurred_reference.astype(dtype)
	return reference_pool


def load_reference_pools(reference_names):
	reference_pools = {}
	for reference_name in reference_names:
		reference_pools[reference_name] = load_reference_pool(f"{util.RESOURCE}/{reference_name}.png")
	return reference_pools
