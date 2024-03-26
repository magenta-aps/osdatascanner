/* exported drawLine */

function makeLineChart(xdata, ydata, chartElement, xLabel = "", swapXY = false, yLabel = "") {

	const chartAreaBorderPlugin = {
		id: 'chartAreaBorder',
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

	const noDataTextDrawPlugin = (ydata.length === 0) ? ({
		id: 'noData',
		afterDatasetsDraw(chart) {
			const {ctx, chartArea: {left, top, width, height}} = chart;
			ctx.save();
			ctx.font = 'bold 20px sans-serif';
			ctx.textAlign = 'center';
			ctx.fillText(gettext('No data available'), left + width / 2, top + height / 2);
		}
	}) : {};

	const lineChart = new Chart(chartElement, {
		type: 'line',
		data: {
			labels: xdata,
			datasets: [{
				data: ydata,
				fill: {
					target: 'origin',
					above: 'rgba(33, 117, 156, 0.5)'
				},
				pointRadius: 0,
				pointHitRadius: 20,
				borderWidth: 4,
				borderCapStyle: 'round',
				tension: 0,
				borderColor: "#21759c",
				pointHoverRadius: 10,
				hoverBackgroundColor: "#21759c",
			}],
		},
		options: {
			plugins: {
				tooltip: {
					enabled: true,
				},
				datalabels: {
					display: false
				},
				legend: false,
				zoom: {
					zoom: {
						limits: {
							x: {min: 'original'}
						},
						wheel: {
							enabled: true,
							modifierKey: 'shift'
						},
						drag: {
							enabled: true,
							threshold: 20,
						},
						pinch: {
							enabled: true
						},
						mode: swapXY ? 'y' : 'x',
					}
				},
			},
			responsive: true,
			maintainAspectRatio: false,
			elements: {
				line: {
					borderJoinStyle: 'round'
				}
			},
			chartArea: {
				backgroundColor: "#f5f5f5"
			},
			scales: {
				x: {
					title: {
						
						display: xLabel !== "",
						text: xLabel,
						labelString: xLabel,
						fontSize: 16,
					},
					gridLines: {
						offsetGridLines: true,
						display: true,
						color: "#fff",
						lineWidth: 3
					},
					ticks: {
						fontSize: 16,
					},
	
				},
				y: {
					beginAtZero: true,
					title: {
						display: yLabel !== "",
						text: yLabel,
						fontSize: 15,
					},
					gridLines: {
						display: false
					},
					ticks: {
						fontSize: 15,
						stepSize: stepSizeFunction(ydata, 2),
					},
				}
			},
		},
		plugins: [
			chartAreaBorderPlugin,
			noDataTextDrawPlugin
		]
	});

	return lineChart;
}

function drawLine(data, ctxName) {
	// Line chart
	// //
	// //
	// //
	// //
	// //
	// Creating xx line chart

	var lineChartLabels = [];
	var lineChartValues = [];

	for (var i = 0; i < data.length; i++) {
		lineChartLabels.push(data[i][0].toUpperCase());
		lineChartValues.push(data[i][1]);
	}

	var lineChartCtx = document.querySelector("#line_chart_" + ctxName).getContext('2d');
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
