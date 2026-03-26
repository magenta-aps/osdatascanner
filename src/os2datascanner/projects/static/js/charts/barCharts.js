/* exported drawBar */

function makeBarChart(chartLabels, chartDatasets, chartElement, swapXY = false, stacked = false) {
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
	if (chartDatasets.length === 0) {
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
	
	const barChart = new Chart(chartElement, {
		type: "bar",
		data: {
			labels: chartLabels,
			datasets: chartDatasets,
		},
		options: {
            indexAxis: swapXY ? "y" : "x",
			responsive: true,
			maintainAspectRatio: false,

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
					limits: swapXY
						? { y: { min: "original" } }
						: { x: { min: "original" } },
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
						mode: swapXY ? "x" : "y",
					}
				},
			},
			scales: {
				x: {
					min: 0,
					stacked: !swapXY && stacked, 
					grid: {
						display: swapXY,
					},
					ticks: {
						font: {
							size: 16
						}
					},
					grace: swapXY ? 1 : 0
				},
				y: {
					min: 0,
					stacked: swapXY && stacked,
					grid: {
						display: !swapXY,
					},
                    ticks: {
						font: {
							size: 16
						}
                    },
					beginAtZero: true,
					grace: swapXY ? 0 : 1
				}
			},
		},
		plugins: plugins,
    });

    return barChart;
}

function drawBar(data, ctxName, labels, swapXY, stacked) {
	// NumBars is each each bar in a barchart, i.e. each month in a year, 
	// and its associated matches.
	const numBars = data.length;
	
	// Name of the id in the template
	const barChartCtx = document
		.querySelector("#bar_chart_" + ctxName)
		.getContext("2d");

	// Swift exit with empty charts, if there is no data. Writes "No data" in chart
	if(!numBars) {
		charts.push(makeBarChart([], [], barChartCtx, swapXY, stacked));
		return;
	}
	
	// Array of colors, changing colors of each dataset in the graph.
	const colorArray = [ "#21759c","#d4efff", "#00496e", "#5ca4cd"];

	// NumStacks is each dataset added, which uses the same labels for the x-axis,
	// i.e. adding both handled matches and total matches for each org-unit in an organization.
	const numStacks = data[0].length - 1;

	// First position in the array should always be the x-axis label of an element in string,
	// i.e. January, MyOrgUnit, Username, etc.
	const barChartLabels = data.map(row => row[0]);

	const barChartDatasets = [...new Array(numStacks).keys()].map(i => ({ 
		"data": [], 
		"label": labels ? labels[i] : undefined
	}));

	// An array element should look like this:
	// ["Name", datasetData1, datasetData2, ..., datasetDataN]
	for (const i of Array(numBars).keys()) {
		for (const j of Array(numStacks).keys()) {
			barChartDatasets[j].data.push(data[i][j + 1]);
		}
	}

	// How the data should look: 
	// [["Jan", 0, 9], ["Feb", 2, 4], ["Mar", 5, 8]]
	// How the dataset should look:
	// [{'label': 'Handled matches', 'data': [0, 2, 5]}, {'label': 'Total matches', 'data': [9, 4, 8]}]

	for (let i=0; i < barChartDatasets.length; i++) {
		barChartDatasets[i].backgroundColor = colorArray[i % colorArray.length]; //Cycles colors in array
	}

	// SwapXY switches the x and y coordinates
	// Stacked changes whether multiple datasets are positioned in front/behind each other 
	charts.push(makeBarChart(barChartLabels, barChartDatasets, barChartCtx, swapXY, stacked));
}

