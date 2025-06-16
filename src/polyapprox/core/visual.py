import pyqtgraph as pg
from . import config,renderer
from .structures import Trace
from multiprocessing import Queue

def build(group_box_plot, self):
	plot_widget = pg.PlotWidget()
	plot_widget.setXRange(0, config.MAX_ITERATION)
	plot_widget.setYRange(0, 1)
	plot_widget.addLegend(offset=(-20, 10))
	plot_widget.setInteractive(False)
	group_box_plot.layout().addWidget(plot_widget)

	logs = [[log] + ["0"] * config.STRATEGY_COUNT for log in ["iteration:", "resolution:", "ssim:"]]
	dashboard = pg.TextItem(anchor=(-0.8, 1.2))
	plot_widget.addItem(dashboard)

	traces = []
	for i in range(config.STRATEGY_COUNT):
		trace = Trace(
			trace_id=i,
			queue=Queue(maxsize=10),
			polygon_count=config.POLYGON_COUNTS[i],
			vertex_count=config.VERTEX_COUNTS[i],
			canvas=getattr(self, f"label_approx{i}"),
			curve=plot_widget.plot([], [], pen=config.CURVE_COLORS[i], name=f"拟合{i + 1}"),
			iterations=[],
			metrics=[],
			cursor=pg.TextItem(anchor=(0, 1), color=config.CURVE_COLORS[i]),
			logs=logs,
			dashboard=dashboard
		)
		traces.append(trace)
		plot_widget.addItem(trace.cursor)
	return traces

def refresh(trace):
	iteration, metric, resolution, approximation_data = trace.queue.get()

	trace.iterations.append(iteration)
	trace.metrics.append(metric)
	trace.curve.setData(trace.iterations, trace.metrics)

	if approximation_data is not None:
		renderer.render_approximation(trace.canvas, approximation_data, resolution)

	trace.cursor.setText(f"{metric:.4f}")
	trace.cursor.setPos(trace.iterations[-1], trace.metrics[-1])

	trace.logs[0][trace.trace_id + 1] = f"{iteration}"
	trace.logs[1][trace.trace_id + 1] = f"{resolution}"
	trace.logs[2][trace.trace_id + 1] = f"{metric:.4f}"
	trace.dashboard.setText("\n".join("\t".join(log) for log in trace.logs))

# 	f"coord_pert\t{self.approximation_thread.approximator.perturbation[0]}\n"
# 	f"color_pert\t{self.approximation_thread.approximator.perturbation[1]}"