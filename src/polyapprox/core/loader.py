import cv2
import numpy as np
from shared import util

from . import config


def load_reference_pool(reference_path, dtype=np.uint8):
	reference = cv2.cvtColor(cv2.imread(reference_path), cv2.COLOR_BGR2RGB)
	reference_pool = {}
	for reference_size, blur_kernel_size in config.BLUR_KERNEL_SIZES.items():
		resized_reference = cv2.resize(reference, (reference_size, reference_size))
		blurred_reference = cv2.GaussianBlur(resized_reference, (blur_kernel_size, blur_kernel_size), 0)
		reference_pool[reference_size] = blurred_reference.astype(dtype)
	return reference_pool


def load_reference_pools():
	reference_pools = {}
	for reference_name in config.PRELOAD_REFERENCE_NAMES:
		reference_pools[reference_name] = load_reference_pool(f"{util.RESOURCE}/{reference_name}.png")
	return reference_pools
