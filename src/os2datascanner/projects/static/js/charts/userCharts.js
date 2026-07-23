function drawUserChart(content) {

  const matchesByWeekElement = content.querySelector('#matches_by_week');
  const accountUuidElement = content.querySelector('#uuid');

  if (!matchesByWeekElement || !accountUuidElement) {
    return;
  }

  const matchesByWeek = JSON.parse(matchesByWeekElement.textContent);
  const accountUuid = JSON.parse(accountUuidElement.textContent);

  let weeknums = [];
  let matches = [];

  for (let obj of matchesByWeek) {
    // Reverse the direction of the arrays with unshift.
    weeknums.unshift(obj.weeknum);
    matches.unshift(obj.matches);
  }

  const UserChartCtx = document.querySelector("#line_chart_all_matches_development__" + accountUuid).getContext('2d');

  makeLineChart(weeknums, matches, UserChartCtx, xLabel = "Uge", yLabel = "Uhåndterede resultater");


}

htmx.onLoad((content) => {
  if (hasClass(content, 'overview_wrapper') || hasClass(content, 'page')) {
    drawUserChart(content);
  }
});
