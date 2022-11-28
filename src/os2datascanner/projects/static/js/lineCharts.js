/* exported drawLines */

function makeLineChart(xdata, ydata, chartElement) {
	// Plugin for coloring the background of the plot
	const backgroundPlugin = {
		id: 'customCanvasBackgroundColor',
		beforeDraw: (chart) => {
		  const {ctx} = chart;
		  ctx.save();
		  ctx.globalCompositeOperation = 'destination-over';
		  ctx.fillStyle = '#f5f5f5';
		  ctx.fillRect(
			chart.chartArea.left, 
			chart.chartArea.top, 
			chart.chartArea.width,
			chart.chartArea.height);
		  ctx.restore();
		}
	  };
	
	const lineChart = new Chart(chartElement, {
		type: 'line',
		data: {
			labels: xdata,
			datasets: [{
				data: ydata,
				fill: 0,
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
					backgroundColor: 'rgba(255, 255, 255, 0.8)',
					borderColor: "rgba(100, 44, 145, 0.8)",
					titleColor: 'black',
					titleAlign: 'center',
					bodyColor: 'black',
					displayColors: false,
					caretSize: 0,
				},
				datalabels: {
					display: false
				},
				legend: false,
				responsive: true,

			},
						
			maintainAspectRatio: false,

			scales: {
				x: {
					grid: {
						offset: true,
						display: true,
						color: "#fff",
						lineWidth: 1
					},
					ticks: {
						font: {
							size: 16
						}
					}
				},
				y: {
					grid: {
						display: true,
						color: "#fff",
						lineWidth: 1
					},
					ticks: {
						font: {
							size: 14
						},
					},
					beginAtZero: true
				}
			}
		},
		plugins: [backgroundPlugin]
	});

	return lineChart;
}

function drawLines(newMatchesByMonth, unhandledMatchesByMonth) {
	// Line chart
	// //
	// //
	// //
	// //
	// //
	// Creating xx line chart

	var newMatchesLineChartLabels = [];
	var newMatchesLineChartValues = [];

	for (var i = 0; i < newMatchesByMonth.length; i++) {
		newMatchesLineChartLabels.push(newMatchesByMonth[i][0].toUpperCase());
		newMatchesLineChartValues.push(newMatchesByMonth[i][1]);
	}

	// Adds empty values in front of both arrays (for styling purposes)
	newMatchesLineChartLabels.unshift("");
	newMatchesLineChartLabels.push("");
	newMatchesLineChartValues.unshift(null);
	newMatchesLineChartValues.push(null);

	var newMatchesLineChartCtx = document.querySelector("#line_chart_new_matches_by_month").getContext('2d');
	charts.push(makeLineChart(newMatchesLineChartLabels, newMatchesLineChartValues, newMatchesLineChartCtx));

	var unhandledMatchesLineChartLabels = [];
	var unhandledMatchesLineChartValues = [];

	for (var j = 0; j < unhandledMatchesByMonth.length; j++) {
		unhandledMatchesLineChartLabels.push(unhandledMatchesByMonth[j][0].toUpperCase());
		unhandledMatchesLineChartValues.push(unhandledMatchesByMonth[j][1]);
	}

	// Adds empty values in front of both arrays (for styling purposes)
	unhandledMatchesLineChartLabels.unshift("");
	unhandledMatchesLineChartLabels.push("");
	unhandledMatchesLineChartValues.unshift(null);
	unhandledMatchesLineChartValues.push(null);

	var unhandledMatchesLineChartCtx = document.querySelector("#line_chart_unhandled_matches").getContext('2d');
	charts.push(makeLineChart(unhandledMatchesLineChartLabels, unhandledMatchesLineChartValues, unhandledMatchesLineChartCtx));
}
