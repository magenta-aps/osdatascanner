/* exported drawTimelines */

function getTimeUnit(maxSeconds) {
  if (maxSeconds >= 172800) {
    return { unitKey: "days", factor: 172800 };
  }
  if (maxSeconds >= 7200) {
    return { unitKey: "hours", factor: 7200 };
  }
  if (maxSeconds >= 120) {
    return { unitKey: "minutes", factor: 120 };
  }
  return { unitKey: "seconds", factor: 1 };
}

function translateUnit(unitKey) {
  const units = {
    seconds: gettext("seconds"),
    minutes: gettext("minutes"),
    hours:   gettext("hours"),
    days:    gettext("days"),
  };
  return units[unitKey] || unitKey;
}


function drawTimelines(snapshotData, pk) {

  let maxSeconds = Math.max(...snapshotData.map(p => p.x));
  let timeUnit = getTimeUnit(maxSeconds);

  const unitLabel = translateUnit(timeUnit.unitKey);

  let timelinesLineChartCtx = document.querySelector(
    "#line_chart_status__" + String(pk)
  );

  if (timelinesLineChartCtx) {
    new Chart(timelinesLineChartCtx, {
      type: "line",
      data: {
        datasets: [{
          data: snapshotData,
          fill: 0,
          tension: 0, // This makes the lines straight, with no curve
          pointRadius: 0,
          pointHitRadius: 20,
          borderWidth: 4,
          borderColor: cssVar("--chart-color-osds-blue"),
          hoverRadius: 0, // Hide hover effect.
          hoverBorderWidth: 0, // Hide hover effect.
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false},
        },
        scales: {
          x: {
            type: "linear",
            min: 0,
            ticks: {
              stepSize: timeUnit.factor, // 60, 3600, 86400 — see getTimeUnit()
              callback: function (value) {
                return value / timeUnit.factor;
              },
            },
            title: {
              display: true,
              text: interpolate(
                gettext("%(unit)s since start of scan"),
                { unit: unitLabel },
                true
              ),
            },
          },
          y: {
            title: {
              display: true,
              text: gettext("% scanned"),
            },
          },
        },
      },
    });
  }
}

function drawPieCharts(bytesData, timeData, pk) {
  const bytesColors = paletteForN(bytesData.length, 0); // green
  const timeColors  = paletteForN(timeData.length, 4);  // purple

  drawPie(bytesData, "bytes_status__" + String(pk), bytesColors);
  drawPie(timeData, "seconds_status__" + String(pk), timeColors);
}

function getNextStatisticRow(row) {
  var sibling = row.nextElementSibling;
  if (sibling.matches(".statistic_row")) {
    return sibling;
  } else {
    return getNextStatisticRow(sibling);
  }
}

function showTimeline(row, toggleButton) {
  let timelinesRow = getNextStatisticRow(row);
  toggleClass(toggleButton, "up");
  let buttonOpen = hasClass(toggleButton, "up");

  timelinesRow.hidden = !buttonOpen;
}

document.addEventListener("DOMContentLoaded", () => {
  window.charts = [];
  htmx.onLoad(function (content) {
    if (hasClass(content, 'page') || hasClass(content, 'content')) {

      const expandButtons = document.querySelectorAll(".timelines-expand");

      expandButtons.forEach(element => {
        element.addEventListener("click", function (e) {
          targ = e.target;
          let row = closestElement(targ, "tr");
          showTimeline(row, targ);
        });
      });
    } else if (hasClass(content, 'timeline')) {
      let snapshotData = JSON.parse(content.querySelector('#snapshot_data').textContent);
      let bytesData = JSON.parse(content.querySelector('#bytes_data').textContent);
      let timeData = JSON.parse(content.querySelector('#time_data').textContent);
      let pk = JSON.parse(content.querySelector('#status_pk').textContent);

      drawTimelines(snapshotData, pk);
      drawPieCharts(bytesData, timeData, pk);
    }
  });
});