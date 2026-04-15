// This is where chart.js specific plugins live.

/* exported chartAreaBorderPlugin, makeNoDataPlugin */

const chartAreaBorderPlugin = {
	id: "chartAreaBorder",
	beforeDraw(chart, _args, options) {
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

function makeNoDataPlugin(isEmpty) {
	if (!isEmpty) { return {}; }
	return {
		id: "noData",
		afterDatasetsDraw(chart) {
			const {ctx, chartArea: {left, top, width, height}} = chart;
			ctx.save();
			ctx.font = "bold 20px sans-serif";
			ctx.textAlign = "center";
			ctx.fillText(gettext("No data available"), left + width / 2, top + height / 2);
			ctx.restore();
		}
	};
}
