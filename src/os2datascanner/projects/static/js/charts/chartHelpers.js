/* exported colorFunction, stepSizeFunction, resetZoomHighest, resetZoomDevelopment, avoidZero */

// Color function
// reads colors from :root
var colorFunction = function (color) {
  "use strict";
  return getComputedStyle(document.querySelector(":root")).getPropertyValue(
    color
  );
};

// Step size function
// Array = values
// steps = how many steps on y-axis ( 0 doesn't count)
var stepSizeFunction = function (array, steps) {
  "use strict";
  return (Math.ceil(Math.max.apply(null, array) / 100) * 100) / steps;
};

// isNan function

var avoidZero = function (a, b) {
  "use strict";
  return isNaN((a / b) * 100) ? 0 + "%" : ((a / b) * 100).toFixed(0) + "%";
};

// Set default animation duration on charts - this can be changed for each chart if needed.
Chart.defaults.animation.easing = "easeOutQuad";
Chart.defaults.animation.duration = 1700;

function drawCharts() {
  // json_script solution - Safe from in-page script execution

  const sourceTypes = JSON.parse(
    document.getElementById("total_by_source").textContent
  );

  const resolutionStatus = JSON.parse(
    document.getElementById("resolution_status").textContent
  );

  const matchData = JSON.parse(
    document.getElementById("match_data").textContent
  );

  const matchesByOrgUnitUnhandled = JSON.parse(
    document.getElementById("matches_by_org_unit_unhandled").textContent
  );
  const matchesByOrgUnitHandled = JSON.parse(
    document.getElementById("matches_by_org_unit_handled").textContent
  );
  const matchesByOrgUnitTotal = JSON.parse(
    document.getElementById("matches_by_org_unit_total").textContent
  );

  const newMatchesByMonth = JSON.parse(
    document.getElementById("new_matches_by_month").textContent
  );

  const unhandledMatchesByMonth = JSON.parse(
    document.getElementById("unhandled_matches_by_month").textContent
  );

  // Finds the total number matches in the array
  totalArrayValue = function (array, index) {
    let number = 0;
    for (let i = 0; i < array.length; i++) {
      number += array[i][index];
    }
    return number;
  };

  // Prepare data for doughnut chart
  const totalHandledMatches = matchData.handled.count;
  const totalMatches = matchData.handled.count + matchData.unhandled.count;
  var handledPercentage = (totalHandledMatches / totalMatches) * 100;

  // Percentage of handled matches
  drawDoughnut(totalHandledMatches, totalMatches, handledPercentage);

  // Distribution of data types and resolution status
  drawPie(sourceTypes, "datasources", [
    "#fed149",
    "#5ca4cd",
    "#21759c",
    "#00496e",
    "#bfe474",
    "#e47483",
  ]);
  drawPie(
    // Change the order of the data structure
    [3, 2, 1, 4, 0].map((i) => resolutionStatus[i]),
    "resolution_status",
    ["#80ab82", "#a2e774", "#35bd57", "#1b512d", "#7e4672"]
  );

  if (
    matchesByOrgUnitHandled &&
    matchesByOrgUnitUnhandled &&
    matchesByOrgUnitTotal
  ) {
    // Org unit distribution
    drawBar(
      matchesByOrgUnitUnhandled,
      "org_unit_highest_unhandled",
      ["Handled matches", "Total matches"],
      true,
      true
    );
    drawBar(matchesByOrgUnitHandled, "org_unit_highest_handled", [], true);
    drawBar(matchesByOrgUnitTotal, "org_unit_highest_total", [], true);
  }

  // New and unhandled matches by month
  drawBar(newMatchesByMonth, "new_matches_by_month");
  drawLine(unhandledMatchesByMonth, "unhandled_matches");
}

function resetZoomHighest() {
  let highestUnhandled = Chart.getChart("bar_chart_org_unit_highest_unhandled");
  let highestHandled = Chart.getChart("bar_chart_org_unit_highest_handled");
  let highestTotal = Chart.getChart("bar_chart_org_unit_highest_total");
  highestUnhandled.resetZoom();
  highestHandled.resetZoom();
  highestTotal.resetZoom();
}
function resetZoomDevelopment() {
  let unhandledMatches = Chart.getChart("line_chart_unhandled_matches");
  let newMatches = Chart.getChart("bar_chart_new_matches_by_month");
  unhandledMatches.resetZoom();
  newMatches.resetZoom();
}

function setStatDropdownEvent() {
  // Target all dropdown elements within the card__header
  const dropdowns = document.querySelectorAll(
    ".card__header-ui .dropdown select"
  );

  dropdowns.forEach((dropdown) => {
    dropdown.addEventListener("change", (e) => {
      const selectedOption = e.target.selectedOptions[0]; // Get selected <option>
      const selectedValue = e.target.value;
      const newSubtitle = selectedOption.dataset.subtitle; // Retrieve the subtitle

      // Get the parent `.card`
      const card = dropdown.closest(".card");

      // Toggle visibility of canvas wrappers
      card
        .querySelectorAll(".canvas__wrapper[data-chartid]")
        .forEach((wrapper) => {
          wrapper.classList.toggle(
            "hidden",
            wrapper.dataset.chartid !== selectedValue
          );
        });

      // Toggle visibility of legends
      card
        .querySelectorAll(".canvas__legend[data-chartid]")
        .forEach((legend) => {
          legend.classList.toggle(
            "hidden",
            legend.dataset.chartid !== selectedValue
          );
        });

      // Update subtitle text dynamically
      const subtitle = card.querySelector(".subtitle");
      if (subtitle) {
        subtitle.textContent = newSubtitle;
      }
    });
  });
}

function clearCharts() {
  for (let chart of charts) {
    chart.destroy();
  }
  charts.length = 0;
}

document.addEventListener("DOMContentLoaded", function () {
  window.charts = [];
});

htmx.onLoad(function (content) {
  if (
    content.className.includes("content") ||
    content.className.includes("page")
  ) {
    clearCharts();
    setStatDropdownEvent();
    setDropdownEvent();
    drawCharts();
  }
});
