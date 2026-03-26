/* exported drawDoughnut */

const centerTextPlugin = {
	id: "doughnutCenterText",
	beforeDraw: function (chart) {
		let ctx, centerConfig, fontStyle, txt, weight, color, maxFontSize, sidePadding, sidePaddingCalculated;
		if (chart.config.options.elements.center) {
			// Get ctx from string
			ctx = chart.ctx;

			// Get options from the center object in options
			centerConfig = chart.config.options.elements.center;
			fontStyle = centerConfig.fontStyle || "Arial";
			txt = centerConfig.text;
			weight = centerConfig.weight;
			color = centerConfig.color || "#000";
			maxFontSize = centerConfig.maxFontSize || 75;
			sidePadding = centerConfig.sidePadding || 20;
			sidePaddingCalculated = (sidePadding / 100) * (chart.getDatasetMeta(0).controller.innerRadius * 2);
			// Start with a base font of 30px
			ctx.font = weight + " 30px " + fontStyle;
		}

		// Get the width of the string and also the width of the element minus 10 to give it 5px side padding
		const stringWidth = ctx.measureText(txt).width;
		const elementWidth = (chart.getDatasetMeta(0).controller.innerRadius * 2) - sidePaddingCalculated;

		// Find out how much the font can grow in width.
		const widthRatio = elementWidth / stringWidth;
		const newFontSize = Math.floor(30 * widthRatio);
		const elementHeight = (chart.getDatasetMeta(0).controller.innerRadius * 2);

		// Pick a new font size so it will not be larger than the height of label.
		let fontSizeToUse = Math.min(newFontSize, elementHeight, maxFontSize);
		let minFontSize = centerConfig.minFontSize;
		const lineHeight = centerConfig.lineHeight || 25;
		let wrapText = false;

		if (minFontSize === undefined) {
			minFontSize = 20;
		}

		if (minFontSize && fontSizeToUse < minFontSize) {
			fontSizeToUse = minFontSize;
			wrapText = true;
		}

		// Set font settings to draw it correctly.
		ctx.save();
		ctx.textAlign = "center";
		ctx.textBaseline = "middle";
		const centerX = ((chart.chartArea.left + chart.chartArea.right) / 2);
		let centerY = ((chart.chartArea.top + chart.chartArea.bottom) / 2);
		ctx.font = weight + " " + fontSizeToUse + "px " + fontStyle;
		ctx.fillStyle = color;

		if (!wrapText) {
			ctx.fillText(txt, centerX, centerY);
			ctx.restore();
			return;
		}

		const words = txt.split(" ");
		let line = "";
		const lines = [];

		// Break words up into multiple lines if necessary
		for (let n = 0; n < words.length; n++) {
			const testLine = line + words[n] + " ";
			const metrics = ctx.measureText(testLine);
			const testWidth = metrics.width;
			if (testWidth > elementWidth && n > 0) {
				lines.push(line);
				line = words[n] + " ";
			} else {
				line = testLine;
			}
		}

		// Move the center up depending on line height and number of lines
		centerY -= (lines.length / 2) * lineHeight;

		for (let m = 0; m < lines.length; m++) {
			ctx.fillText(lines[m], centerX, centerY);
			centerY += lineHeight;
		}
		//Draw text in center
		ctx.fillText(line, centerX, centerY);
		ctx.restore();
	}
};

const roundedCornersPlugin = {
	id: "doughnutRoundedCorners",
	afterUpdate: function (chart) {
		if (chart.config.options.elements.arc.roundedCornersFor !== undefined) {
			const arc = chart.getDatasetMeta(0).data[chart.config.options.elements.arc.roundedCornersFor];
			arc.round = {
				x: (chart.chartArea.left + chart.chartArea.right) / 2,
				y: (chart.chartArea.top + chart.chartArea.bottom) / 2,
				radius: (arc.outerRadius + arc.innerRadius) / 2,
				thickness: (arc.outerRadius - arc.innerRadius) / 2,
				backgroundColor: arc.options.backgroundColor
			};
		}
	},

	afterDraw: function (chart) {
		if (chart.config.options.elements.arc.roundedCornersFor !== undefined) {
			const ctx = chart.ctx;
			const arc = chart.getDatasetMeta(0).data[chart.config.options.elements.arc.roundedCornersFor];
			const startAngle = Math.PI / 2 - arc.startAngle;
			const endAngle = Math.PI / 2 - arc.endAngle;

			ctx.save();
			ctx.translate(arc.round.x, arc.round.y);
			ctx.fillStyle = arc.round.backgroundColor;
			ctx.beginPath();
			ctx.arc(arc.round.radius * Math.sin(startAngle), arc.round.radius * Math.cos(startAngle), arc.round.thickness, 0, 2 * Math.PI);
			ctx.arc(arc.round.radius * Math.sin(endAngle), arc.round.radius * Math.cos(endAngle), arc.round.thickness, 0, 2 * Math.PI);
			ctx.closePath();
			ctx.fill();
			ctx.restore();
		}
	},
};

function makeDoughnutChart(text, data, colors, chartElement) {
	const doughnutChart = new Chart(chartElement, {
		type: "doughnut",
		data: {
			datasets: [{
				data: data,
				backgroundColor: colors,
				borderWidth: 0
			}]
		},
		options: {
			layout: {
				padding: {
				  left: 8,
				  right: 8,
				  top: 8,
				  bottom: 8
				}
			  },
			cutout: "75%",
			elements: {
				arc: {
					roundedCornersFor: 0
				},
				center: {
					minFontSize: 16,
					maxFontSize: 32,
					weight: "bold",
					text: text,
				}
			},
			plugins: {
				datalabels: {
					display: false
				},
			},
			events: [],
			responsive: true,
			aspectRatio: 1,
			maintainAspectRatio: false
		},
		plugins: [centerTextPlugin, roundedCornersPlugin],
	});

	return doughnutChart;
}

function drawDoughnut(totalHandledMatches, totalMatches, handledPercentage) {
	const totalHandledDoughnutChartCtx = document.querySelector("#doughnut_chart_total").getContext("2d");
	// Only show the "blue" ring when the percentage is 1 or above:
	const blueColor = (!isNaN(handledPercentage) && handledPercentage >= 1) ? "#21759c" : "transparent";
	charts.push(makeDoughnutChart(
		// logic to avoid 0 divided by 0 being NaN
		isNaN(handledPercentage) ? gettext("No data") : handledPercentage.toFixed(0) + "%",
		[totalHandledMatches, (totalMatches - totalHandledMatches)],
		[blueColor, "#f5f5f5"],
		totalHandledDoughnutChartCtx
	));
}
