// Line chart
// // 
// // 
// // 
// // 
// // 
// Creating xx line chart

Chart.pluginService.register({
	// This works to color the background
	beforeDraw: function (chart, easing) {

	if (chart.config.options.chartArea && chart.config.options.chartArea.backgroundColor) {
		var ctx = chart.chart.ctx;
		var chartArea = chart.chartArea;

		var meta = chart.getDatasetMeta(0);

		// half the width of a 'bar'
		var margin = (meta.data[1]._model.x-meta.data[0]._model.x)/2;
		
		// Position at index 2 - margin (index 0 is null) 
		var start = meta.data[1]._model.x-margin;

		var stop  = meta.data[meta.data.length-1]._model.x-margin;
		
		ctx.save();
		ctx.fillStyle = chart.config.options.chartArea.backgroundColor;

		ctx.fillRect(start, chartArea.top, stop - start, chartArea.bottom - chartArea.top);
		ctx.restore();
		}
	}
});

var testData = [ null, 5, 10, 18, 33, 121, 184, 179, 196, 158, 166, 66, 20, null];
  
var newMatchesLineChartCtx = document.querySelector("#line_chart_new_matches").getContext('2d');
new Chart(newMatchesLineChartCtx, {
	type: 'line',
	data: {
		labels: ["", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", ""],
		datasets: [{
			data: [ null, 5, 10, 18, 33, 121, 184, 179, 196, 158, 166, 66, 20, null],
			fill: 0,
			pointRadius: 0,
			pointHitRadius: 20,
			borderWidth: 4,
			borderCapStyle: 'round',
			tension: 0,
			borderColor: colorFunction('--color-icon-primary'),
			pointHoverRadius: 10,
			hoverBackgroundColor: colorFunction('--color-icon-primary'),
		}],
	},
	options: {
		tooltips: {
			// Disable the on-canvas tooltip
			enabled: false,
	
			custom: function(tooltipModel) {
				// Tooltip Element
				var tooltipEl = document.getElementById('line-chart-new-matches-tooltip');
	
				// Create element on first render
				if (!tooltipEl) {
					tooltipEl = document.createElement('div');
					tooltipEl.id = 'line-chart-new-matches-tooltip';
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
					var titleLines = tooltipModel.title || [];
					var bodyLines = tooltipModel.body.map(getBody);
	
					var innerHtml = '<thead>';
	
					titleLines.forEach(function(title) {
						innerHtml += '<tr><th>' + title + '</th></tr>';
					});
					innerHtml += '</thead><tbody>';
	
					bodyLines.forEach(function(body, i) {
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
				tooltipEl.style.top = position.top + window.pageYOffset + tooltipModel.caretY + 'px';
				tooltipEl.style.fontFamily = tooltipModel._bodyFontFamily;
				tooltipEl.style.fontSize = '1rem';
				tooltipEl.style.fontStyle = tooltipModel._bodyFontStyle;
				tooltipEl.style.padding = tooltipModel.yPadding + 'px ' + tooltipModel.xPadding + 'px';
				tooltipEl.style.pointerEvents = 'none';
				tooltipEl.style.borderRadius = '3px';
				tooltipEl.style.backgroundColor = 'rgba(255,255,255, 0.8)';
			}
		},
		plugins: {
			datalabels: {
				display: false
			}
		},
		legend: false,
		responsive: true,
		maintainAspectRatio: true,
		elements: {
			line: {
				borderJoinStyle: 'round'
			}
		},
		chartArea: {
			backgroundColor: colorFunction('--color-grey-light')
		},
		scales: {
			xAxes: [{
				gridLines: {
					offsetGridLines: true,
					display: true,                
					color: colorFunction('--color-white'),
					lineWidth: 3
				},
				ticks: {
					fontSize: 16,
				}
			}],
			yAxes: [{
				gridLines: {
					display: false
				},
				ticks: {
					beginAtZero: true,
					fontSize: 14,
					stepSize: stepSizeFunction(testData, 2),
				}
			}]
		},
	}
});