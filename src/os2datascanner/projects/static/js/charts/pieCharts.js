/* exported drawPie */

function makePieChart(labels, data, colors, chartElement) {
  const isEmptyChart = data.length === 1 && labels[0] === "No Data";
  const isSingleValue = data.filter((val) => val > 0).length === 1;

  const pieChart = new Chart(chartElement, {
    type: "pie",
    data: {
      labels: labels,
      datasets: [
        {
          data: data,
          backgroundColor: colors,
          borderWidth: 0,
          borderAlign: "center",
          hoverOffset: isEmptyChart || isSingleValue ? 0 : 16,
        },
      ],
    },
    options: {
      layout: {
        padding: {
          left: 8,
          right: 8,
          top: 8,
          bottom: 8,
        },
      },
      events: ["mousemove", "mouseout"],
      plugins: {
        datalabels: {
          display: false,
        },
        legend: {
          display: false,
        },
        tooltip: {
          events: ["mousemove", "mouseout"],
          enabled: true,
          backgroundColor: "rgba(255, 255, 255, 1)",
          titleColor: "rgba(0, 0, 0, 1)",
          titleFont: {
            size: 16,
          },
          bodyColor: "rgba(0, 0, 0, 1)",
          bodyFont: {
            size: 16,
          },
          padding: 12,
          caretSize: 0,
          displayColors: false,
          callbacks: {
            title: function (tooltipItems) {
              if (isEmptyChart) {
                return gettext("No data"); // Show custom title for empty charts
              }
              return tooltipItems[0].label;
            },
            label: function (context) {
              if (isEmptyChart) {
                return null; // Prevent any labels from appearing for empty charts
              }

              let value = context.parsed ? context.parsed : 0;
              if (!context.parsed) {
                return null; // prevent the tooltip from showing for slices with 0 value
              }

              const dataArr = context.chart.data.datasets[0].data;
              const sum = dataArr.reduce((total, frac) => total + frac);

              return ((value / sum) * 100).toFixed(2) + "%";
            },
          },
        },
      },
      responsive: true,
      aspectRatio: 1,
      maintainAspectRatio: false,
    },
    plugins: [ChartDataLabels],
  });

  return pieChart;
}

function drawPie(data, ctxName, colors) {
  const totalValue = Object.values(data).reduce(
    (sum, obj) => sum + (obj.count || 0),
    0
  );

  const filteredData = Object.values(data).filter((obj) => obj.count); // Filter out entries with a count of 0

  const labels = totalValue
    ? filteredData.map(
        (obj) => obj.label.charAt(0).toUpperCase() + obj.label.slice(1)
      )
    : [gettext("No Data")];
  const values = totalValue ? filteredData.map((obj) => obj.count) : [1];

  const colorPredicate = (color, index) => Object.values(data)[index].count;
  const chartColors = totalValue ? colors.filter(colorPredicate) : ["#e0e0e0"]; // Determine the chart colors based on available data

  const pieChartCtx = document
    .querySelector("#pie_chart_" + ctxName)
    .getContext("2d");
  const pieChart = makePieChart(labels, values, chartColors, pieChartCtx);

  charts.push(pieChart);

  $("#pie_legend_" + ctxName).html(unorderedListLegend(data, colors, pieChart)); // Generate the legend from the original data regardless of the pie chart state
}

function unorderedListLegend(data, colors, chart) {
  let text = [`<ul id="${chart.id}" class="canvas-legend">`];

  // Get the total of all non-zero data points
  const totalValue = Object.values(data).reduce(
    (sum, obj) => sum + (obj.count || 0),
    0
  );

  Object.values(data).forEach((obj, index) => {
    const value = obj.count;
    const label = obj.label.charAt(0).toUpperCase() + obj.label.slice(1);
    const backgroundColor = colors[index];

    // Calculate percentage based on totalValue
    const percentage = value
      ? ((value / totalValue) * 100).toFixed(2) + "%"
      : "0%";

    if (value > 0) {
      text.push(
        `<li class="canvas-legend__item">
          <i id="circle" class="material-symbols canvas-legend__bullet" style="color:${backgroundColor}">circle</i>`
      );
      if (label) {
        text.push(
          `<p class="canvas-legend__label">
            ${label} - ${percentage}
          </p>`
        );
      }
      text.push("</li>");
    }
  });
  text.push("</ul>");
  return text.join("");
}