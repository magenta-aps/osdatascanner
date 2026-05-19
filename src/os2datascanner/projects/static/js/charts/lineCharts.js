/* exported drawLine */

function makeLineChart(xdata, ydata, chartElement, xLabel = "", swapXY = false, yLabel = "") {
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
						display: true,
						color: function(context) {
							const ticks = context.scale.ticks;
							const isFirstOrLast = context.index === 0 || context.index === ticks.length - 1;
							return isFirstOrLast ? Chart.defaults.borderColor : "transparent";
						},
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
		plugins: [...(ydata.length === 0 ? [noDataPlugin] : [])],
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
