/* exported drawLine */

function makeLineChart(xdata, ydata, chartElement, xLabel = "", swapXY = false, yLabel = "") {

	const chartAreaBorderPlugin = {
		id: "chartAreaBorder",
		beforeDraw(chart, args, options) {
			const {ctx, chartArea: {left, top, width, height}} = chart;
			ctx.save();
			ctx.strokeStyle = options.borderColor;
			ctx.lineWidth = options.borderWidth;
			ctx.setLineDash(options.borderDash || []);
			ctx.lineDashOffset = options.borderDashOffset;
			ctx.strokeRect(left, top, width, height);
			ctx.restore();
		}
	};

	const plugins = [chartAreaBorderPlugin];
	if (ydata.length === 0) {
		plugins.push({
			id: "noData",
			afterDatasetsDraw(chart) {
				const {ctx, chartArea: {left, top, width, height}} = chart;
				ctx.save();
				ctx.font = "bold 20px sans-serif";
				ctx.textAlign = "center";
				ctx.fillText(gettext("No data available"), left + width / 2, top + height / 2);
				ctx.restore();
			}
		});
	}

	const lineChart = new Chart(chartElement, {
		type: "line",
		data: {
			labels: xdata,
			datasets: [{
				data: ydata,
				fill: {
					target: "origin",
					above: "rgba(33, 117, 156, 0.5)"
				},
				pointRadius: 0,
				pointHitRadius: 20,
				borderWidth: 4,
				borderCapStyle: "round",
				tension: 0,
				borderColor: "#21759c",
				pointHoverRadius: 10,
				hoverBackgroundColor: "#21759c",
			}],
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			
			elements: {
				line: {
					borderJoinStyle: "round"
				}
			},

			plugins: {
				tooltip: {
					enabled: true,
				},
				datalabels: {
					display: false
				},
				legend: {
					display: false
				},
				chartAreaBorder: {
					borderColor: "lightgray",
					borderWidth: 1,
				},
				zoom: {
					limits: {
						x: {min: "original"}
					},
					zoom: {
						wheel: {
							enabled: true,
							modifierKey: "shift"
						},
						drag: {
							enabled: true,
							threshold: 20,
						},
						pinch: {
							enabled: true
						},
						mode: swapXY ? "y" : "x",
					}
				},
			},

			scales: {
				x: {
					title: {
						display: xLabel !== "",
						text: xLabel,
						font: {
							size: 14,
						},
					},
					grid: {
						offset: true,
						display: true,
						lineWidth: 1,
					},
					ticks: {
						font: {
							size: 14,
						},
					},
	
				},
				y: {
					beginAtZero: true,
					title: {
						display: yLabel !== "",
						text: yLabel,
						font: {
							size: 14,
						},
					},
					grid: {
						display: false
					},
					ticks: {
						font: {
							size: 15,
						},
						stepSize: stepSizeFunction(ydata, 2),
					},
				}
			},
		},
		plugins: plugins,
	});

	return lineChart;
}

function drawLine(data, ctxName) {

	var lineChartLabels = [];
	var lineChartValues = [];

	for (var i = 0; i < data.length; i++) {
		lineChartLabels.push(data[i][0].toUpperCase());
		lineChartValues.push(data[i][1]);
	}

	const lineChartCtx = document
		.querySelector("#line_chart_" + ctxName)
		.getContext("2d");

	charts.push(makeLineChart(lineChartLabels, lineChartValues, lineChartCtx));
}

// Step size function
// Array = values
// steps = how many steps on y-axis ( 0 doesn't count)
var stepSizeFunction = function (array, steps) {
	"use strict";
	if (array.length === 0) {
		return 0.1;
	}
	return (Math.ceil(Math.max.apply(null, array) / 100) * 100) / steps;
};
