/* exported drawBars */

function drawBars(newMatchesByMonth, unhandledMatchesByMonth) {
	// Bar chart
	// //
	// //
	// //
	// //
	// //
	// Creating xx Bar chart

	// Chart.pluginService.register({
	// 	// This works to color the background
	// 	beforeDraw: function (chart) {

	// 		if (chart.config.options.chartArea && chart.config.options.chartArea.backgroundColor) {
	// 			var ctx = chart.chart.ctx;
	// 			var chartArea = chart.chartArea;

	// 			var meta = chart.getDatasetMeta(0);

	// 			// half the width of a 'bar'
	// 			var margin = (meta.data[1]._model.x - meta.data[0]._model.x) / 2;

	// 			// Position at index 2 - margin (index 0 is null)
	// 			var start = meta.data[0]._model.x - margin;

	// 			var stop = meta.data[meta.data.length - 1]._model.x - margin;

	// 			ctx.save();
	// 			ctx.fillStyle = chart.config.options.chartArea.backgroundColor;

	// 			ctx.fillRect(start, chartArea.top, stop - start, chartArea.bottom - chartArea.top);
	// 			ctx.restore();
	// 		}
	// 	}
	// });

	var newMatchesBarChartLabels = [];
	var newMatchesBarChartValues = [];

	for (var i = 0; i < newMatchesByMonth.length; i++) {
		newMatchesBarChartLabels.push(newMatchesByMonth[i][0].toUpperCase());
		newMatchesBarChartValues.push(newMatchesByMonth[i][1]);
	}

	var newMatchesBarChartCtx = document.querySelector("#bar_chart_new_matches_by_month").getContext('2d');
	charts.push(new Chart(newMatchesBarChartCtx, {
		type: 'bar',
		data: {
			labels: newMatchesBarChartLabels,
			datasets: [{
				data: newMatchesBarChartValues,
				fill: 0,
				backgroundColor: "#21759c",
				borderWidth: 4,
				tension: 0,
				borderColor: "#21759c",
			}],
		},
		options: {
			tooltips: {
				// Disable the on-canvas tooltip
				enabled: false,

				custom: function (tooltipModel) {
					// Tooltip Element
					var tooltipEl = document.getElementById('bar-chart-new-matches-tooltip');

					// Create element on first render
					if (!tooltipEl) {
						tooltipEl = document.createElement('div');
						tooltipEl.id = 'bar-chart-new-matches-tooltip';
						tooltipEl.innerHTML = '<table></table>';
						document.body.appendChild(tooltipEl);
					}

					// Hide if no tooltip
					if (tooltipModel.opacity === 0) {
						tooltipEl.style.opacity = 0;
						return;
					}

					// Set caret Position
					tooltipEl.classList.remove('above', 'below', 'no-transform');
					if (tooltipModel.yAlign) {
						tooltipEl.classList.add(tooltipModel.yAlign);
					} else {
						tooltipEl.classList.add('no-transform');
					}

					function getBody(bodyItem) {
						return bodyItem.lines;
					}

					// Set Text
					if (tooltipModel.body) {
						var titleBars = tooltipModel.title || [];
						var bodyBars = tooltipModel.body.map(getBody);

						var innerHtml = '<thead>';

						titleBars.forEach(function (title) {
							innerHtml += '<tr><th>' + title + '</th></tr>';
						});
						innerHtml += '</thead><tbody>';

						bodyBars.forEach(function (body, i) {
							var colors = tooltipModel.labelColors[i];
							var style = 'background:' + colors.backgroundColor;
							style += '; border-color:' + colors.borderColor;
							style += '; border-width: 2px';
							var span = '<span style="' + style + '"></span>';
							innerHtml += '<tr><td>' + span + body + '</td></tr>';
						});
						innerHtml += '</tbody>';

						var tableRoot = tooltipEl.querySelector('table');
						tableRoot.innerHTML = innerHtml;
					}

					// `this` will be the overall tooltip
					var position = this._chart.canvas.getBoundingClientRect();

					// Display, position, and set styles for font
					tooltipEl.style.opacity = 1;
					tooltipEl.style.position = 'absolute';
					tooltipEl.style.left = position.left + window.pageXOffset + tooltipModel.caretX + 'px';
					tooltipEl.style.top = position.top + window.pageYOffset + 'px';
					tooltipEl.style.fontFamily = tooltipModel._bodyFontFamily;
					tooltipEl.style.fontSize = '1rem';
					tooltipEl.style.fontStyle = tooltipModel._bodyFontStyle;
					tooltipEl.style.padding = tooltipModel.yPadding + 'px ' + tooltipModel.xPadding + 'px';
					tooltipEl.style.pointerEvents = 'none';
					tooltipEl.style.borderRadius = '3px';
					tooltipEl.style.backgroundColor = 'rgba(255,255,255, 1)';
					tooltipEl.style.boxShadow = '10px 10px 30px #0000001A';
				}
			},
			plugins: {
				datalabels: {
					display: false
				}
			},
			legend: false,
			responsive: true,
			maintainAspectRatio: false,
			elements: {
				bar: {
					borderJoinStyle: 'round'
				}
			},
			chartArea: {
				backgroundColor: "#f5f5f5"
			},
			scales: {
				x: {
					stacked: true
				},
				xAxes: [{
					gridBars: {
						offsetGridBars: true,
						display: true,
						color: "#fff",
						barWidth: 3
					},
					ticks: {
						fontSize: 16,
					}
				}],
				yAxes: [{
					gridBars: {
						display: false
					},
					ticks: {
						beginAtZero: true,
						fontSize: 14,
						stepSize: stepSizeFunction(newMatchesBarChartValues, 2),
					}
				}]
			},
		}
	}));

	var unhandledMatchesBarChartLabels = [];
	var unhandledMatchesBarChartValues = [];

	for (var j = 0; j < unhandledMatchesByMonth.length; j++) {
		unhandledMatchesBarChartLabels.push(unhandledMatchesByMonth[j][0].toUpperCase());
		unhandledMatchesBarChartValues.push(unhandledMatchesByMonth[j][1]);
	}

	var unhandledMatchesBarChartCtx = document.querySelector("#bar_chart_unhandled_matches").getContext('2d');
	charts.push(new Chart(unhandledMatchesBarChartCtx, {
		type: 'bar',
		data: {
			labels: unhandledMatchesBarChartLabels,
			datasets: [{
				data: unhandledMatchesBarChartValues,
				borderWidth: 4,
				tension: 0,
				borderColor: "#21759c",
				backgroundColor: "#21759c",
			}],
		},
		options: {
			tooltips: {
				// Disable the on-canvas tooltip
				enabled: false,

				custom: function (tooltipModel) {
					// Tooltip Element
					var tooltipEl = document.getElementById('bar-chart-new-matches-tooltip');

					// Create element on first render
					if (!tooltipEl) {
						tooltipEl = document.createElement('div');
						tooltipEl.id = 'bar-chart-new-matches-tooltip';
						tooltipEl.innerHTML = '<table></table>';
						document.body.appendChild(tooltipEl);
					}

					// Hide if no tooltip
					if (tooltipModel.opacity === 0) {
						tooltipEl.style.opacity = 0;
						return;
					}

					// Set caret Position
					tooltipEl.classList.remove('above', 'below', 'no-transform');
					if (tooltipModel.yAlign) {
						tooltipEl.classList.add(tooltipModel.yAlign);
					} else {
						tooltipEl.classList.add('no-transform');
					}

					function getBody(bodyItem) {
						return bodyItem.lines;
					}

					// Set Text
					if (tooltipModel.body) {
						var titleBars = tooltipModel.title || [];
						var bodyBars = tooltipModel.body.map(getBody);

						var innerHtml = '<thead>';

						titleBars.forEach(function (title) {
							innerHtml += '<tr><th>' + title + '</th></tr>';
						});
						innerHtml += '</thead><tbody>';

						bodyBars.forEach(function (body, i) {
							var colors = tooltipModel.labelColors[i];
							var style = 'background:' + colors.backgroundColor;
							style += '; border-color:' + colors.borderColor;
							style += '; border-width: 2px';
							var span = '<span style="' + style + '"></span>';
							innerHtml += '<tr><td>' + span + body + '</td></tr>';
						});
						innerHtml += '</tbody>';

						var tableRoot = tooltipEl.querySelector('table');
						tableRoot.innerHTML = innerHtml;
					}

					// `this` will be the overall tooltip
					var position = this._chart.canvas.getBoundingClientRect();

					// Display, position, and set styles for font
					tooltipEl.style.opacity = 1;
					tooltipEl.style.position = 'absolute';
					tooltipEl.style.left = position.left + window.pageXOffset + tooltipModel.caretX + 'px';
					tooltipEl.style.top = position.top + window.pageYOffset + 'px';
					tooltipEl.style.fontFamily = tooltipModel._bodyFontFamily;
					tooltipEl.style.fontSize = '1rem';
					tooltipEl.style.fontStyle = tooltipModel._bodyFontStyle;
					tooltipEl.style.padding = tooltipModel.yPadding + 'px ' + tooltipModel.xPadding + 'px';
					tooltipEl.style.pointerEvents = 'none';
					tooltipEl.style.borderRadius = '3px';
					tooltipEl.style.backgroundColor = 'rgba(255,255,255, 1)';
					tooltipEl.style.boxShadow = '10px 10px 30px #0000001A';
				}
			},
			plugins: {
				datalabels: {
					display: false
				}
			},
			legend: false,
			responsive: true,
			maintainAspectRatio: false,
			elements: {
				bar: {
					borderJoinStyle: 'round'
				}
			},
			chartArea: {
				backgroundColor: "#f5f5f5"
			},
			scales: {
				xAxes: [{
					gridBars: {
						offsetGridBars: true,
						display: true,
						color: "#fff",
						barWidth: 3
					},
					ticks: {
						fontSize: 16,
					}
				}],
				yAxes: [{
					gridBars: {
						display: false
					},
					ticks: {
						beginAtZero: true,
						fontSize: 14,
						stepSize: stepSizeFunction(unhandledMatchesBarChartValues, 2),
					}
				}]
			},
		}
	}));
}
