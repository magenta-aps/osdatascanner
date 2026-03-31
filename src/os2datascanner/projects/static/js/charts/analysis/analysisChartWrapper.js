function drawBars(){
  const dataElement = document.getElementById("chart_data");
  if (typeof dataElement !== "undefined" && dataElement.textContent !== '""'){
    const Data = JSON.parse(dataElement.textContent);
    JSON.parse(Data).forEach((dataset, i) => {
      let ctx = document.getElementById("bar"+(i+1).toString());
      let [data, binSize] = getData(dataset.sizes);
      let title = dataset.type.charAt(0).toUpperCase() + dataset.type.slice(1);
      charts.push(createBars(data, ctx, title, binSize));
    });
  }
}

function drawPies() {
  const colorList = ANALYSIS_COLORS;
  // using json_script to get context data here
  const dataElement = document.getElementById("chart_data");
  if (typeof dataElement !== "undefined" && dataElement.textContent !== '""'){
    const Data = JSON.parse(dataElement.textContent);
    const ctx1 = document.getElementById("pie1");
    const ctx2 = document.getElementById("pie2");
    const types = JSON.parse(Data).map(object => object.type);
    const nFiles = JSON.parse(Data).map(object => object.n_files); // jshint ignore:line
    const totalSize = JSON.parse(Data).map(object => object.total_size); // jshint ignore:line
    const pie1Data = {labels: types, data: nFiles, name: "nfiles", title: gettext("Number of files")};
    const pie2Data = {labels: types, data: totalSize, name: "storage", title: gettext("Storage space")};
    charts.push(createPie(pie1Data, [ctx1, "#pie1"], colorList));
    charts.push(createPie(pie2Data, [ctx2, "#pie2"], colorList));
  }
}

function clearCharts() {
    for (let chart of charts) {
      chart.destroy();
    }
    charts.length = 0;
}


document.addEventListener("DOMContentLoaded", function () {
  htmx.onLoad(function (content) {
    if (content.classList.contains("page")||content.classList.contains("content")){
      clearCharts();
      drawPies();
      drawBars();
    }
  });

  window.charts = [];
});
