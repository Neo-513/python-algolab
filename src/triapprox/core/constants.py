from .structures import Sched

TRIANGLE_COUNT = 50
MAX_ITERATION = 100000

STAGES = [
	Sched.Stage(resolution=16, blur_kernel_size=5, advance_threshold=0.8),
	Sched.Stage(resolution=32, blur_kernel_size=3, advance_threshold=0.75),
	Sched.Stage(resolution=64, blur_kernel_size=1, advance_threshold=0.65),
	Sched.Stage(resolution=128, blur_kernel_size=1, advance_threshold=0.8)
]
INITIAL_RESOLUTION = STAGES[0].resolution
FINAL_RESOLUTION = STAGES[-1].resolution

STRATEGIES = {
	16: [
		Sched.Strategy(threshold=0.00, perturb=Sched.Perturb(vertices=10, color=30))
	],
	32: [
		Sched.Strategy(threshold=0.00, perturb=Sched.Perturb(vertices=8, color=25))
	],
	64: [
		Sched.Strategy(threshold=0.60, perturb=Sched.Perturb(vertices=4, color=15)),
		Sched.Strategy(threshold=0.00, perturb=Sched.Perturb(vertices=6, color=20))
	],
	128: [
		Sched.Strategy(threshold=0.74, perturb=Sched.Perturb(vertices=1, color=1)),
		Sched.Strategy(threshold=0.73, perturb=Sched.Perturb(vertices=1, color=2)),
		Sched.Strategy(threshold=0.72, perturb=Sched.Perturb(vertices=1, color=3)),
		Sched.Strategy(threshold=0.71, perturb=Sched.Perturb(vertices=1, color=4)),
		Sched.Strategy(threshold=0.70, perturb=Sched.Perturb(vertices=1, color=5)),
		Sched.Strategy(threshold=0.68, perturb=Sched.Perturb(vertices=1, color=6)),
		Sched.Strategy(threshold=0.66, perturb=Sched.Perturb(vertices=1, color=7)),
		Sched.Strategy(threshold=0.60, perturb=Sched.Perturb(vertices=8, color=8)),
		Sched.Strategy(threshold=0.58, perturb=Sched.Perturb(vertices=8, color=8)),
		Sched.Strategy(threshold=0.56, perturb=Sched.Perturb(vertices=4, color=9)),
		Sched.Strategy(threshold=0.00, perturb=Sched.Perturb(vertices=4, color=10))
	]
}
INITIAL_PERTURB = STRATEGIES[INITIAL_RESOLUTION][-1].perturb
FINAL_PERTURB = STRATEGIES[FINAL_RESOLUTION][0].perturb
