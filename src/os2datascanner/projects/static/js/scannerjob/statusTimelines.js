/* exported drawTimelines */

function getTimeUnit(maxSeconds) {
  if (maxSeconds >= 86400) {
    return { unitKey: "days", factor: 86400 };
  }
  if (maxSeconds >= 3600) {
    return { unitKey: "hours", factor: 3600 };
  }
  if (maxSeconds >= 60) {
    return { unitKey: "minutes", factor: 60 };
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


/*** CHART COLOURS ***/
/*
 - Builds the chart palette from CSS vars (expected to be defined on :root).
 - Order: grouped by base colour, then suffixes.
 - Example (with current suffixes): green-dark, green, green-light, turquoise-dark, ...
 - Re-enable "-darker" / "-lighter" in `suffixes` if we need more distinct colours.
*/

// Reads a CSS var from :root.
function cssVar(name) {
  return getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim();
}

function getChartPalette(startBaseIndex = 0) {
  // Base order matters: `startBaseIndex` rotates this list for the second chart.
  const bases = [
    "green",
    "turquoise",
    "osds-blue",
    "blue",
    "purple",
    "mauve",
    "red",
    "orange",
    "yellow",
  ];

  // "-darker" and "-lighter" are intentionally disabled to reduce shades per hue.
  // Palette size = bases.length × suffixes.length.
  // Current: 9 × 3 = 27 colours.
  const suffixes = [
    // "-darker", 
    "-dark", 
    "", 
    "-light", 
    // "-lighter",
  ];

  const rotatedBases = bases
    .slice(startBaseIndex)
    .concat(bases.slice(0, startBaseIndex));

  const colors = [];

  for (const base of rotatedBases) {
    for (const suffix of suffixes) {
      const token = `--chart-color-${base}${suffix}`;
      const value = cssVar(token);
      if (value) { 
        colors.push(value);
      }
    }
  }

  return colors;
}

function paletteForN(n, startBaseIndex = 0) {
  // Return an array of N colours.
  // If N exceeds palette length, colours repeat (intentional fallback).
  const palette = getChartPalette(startBaseIndex);
  const out = [];

  for (let i = 0; i < n; i++) {
    out.push(palette[i % palette.length]);
  }

  return out;
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
          pointHoverRadius: 10,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
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