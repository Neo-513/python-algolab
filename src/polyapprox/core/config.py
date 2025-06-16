import numpy as np

MAX_ITERATION = 100000 * 3
POLYGON_COUNTS = (50, 25, 15)#(50, 35, 25)
VERTEX_COUNTS = (3, 6, 10)#(3, 4, 5)
STRATEGY_COUNT = 3

SUPPORTED_RESOLUTIONS = (16, 32, 64, 128)
INITIAL_RESOLUTION = SUPPORTED_RESOLUTIONS[0]
FINAL_RESOLUTION = SUPPORTED_RESOLUTIONS[-1]

BLUR_KERNEL_SIZES = {16: 5, 32: 3, 64: 1, 128: 1}
STAGE_THRESHOLDS = {16: 0.8, 32: 0.75, 64: 0.65, 128: 0.85}
CHANNEL_RGBA_TO_BGRA = [2, 1, 0, 3]

CURVE_COLORS = ("r", "g", "y")
PRELOAD_REFERENCE_NAMES = ("mona_lisa", "firefox", "darwin")
BACKDROP = {resolution: np.zeros((resolution, resolution, 3), dtype=np.uint8) for resolution in SUPPORTED_RESOLUTIONS}  # float32

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