import jsonData from './data.json' assert {type: 'json'} // jshint ignore:line


function displayAsPercentage(value, ctx) {
  let dataArr = ctx.chart.data.datasets[0].data;
  let sum = dataArr.reduce(function (total, frac) { return total + frac; });
  var percentage = Math.round(value * 100 / sum) + "%";
  return value ? percentage : '';
}

function unorderedListLegend(chart) {
  var text = [];
  text.push('<ul id="' + chart.id + '" class="chart-legend">');
  for (var i = 0; i < chart.data.datasets[0].data.length; i++) {
    text.push('<li><span class="bullet" style="color:' + chart.data.datasets[0].backgroundColor[i] + '">&#8226;</span>');
    if (chart.data.labels[i]) {
      text.push(`<span> ${displayLabelUnit(i, chart.data)}`);
    }
    text.push('</span></li>');
  }
  text.push('</ul>');
  return text.join("");
}

function displayLabelUnit(index, chartObject) {
  let dataset = chartObject.datasets[0];
  let labelName = chartObject.labels[index];
  if (dataset.name === "nfiles"){
    return `${labelName}: ${formatNumber(dataset.data[index])} files`;
  }
  else if (dataset.name === "storage"){
    return `${labelName}: ${bytesToSize(dataset.data[index])}`;
  }
  else {
    return `${labelName}: ${formatNumber(dataset.data[index])}`;
  }
}

function LegendClickCallback(event) {
  event = event || window.event;
  var target = event.target || event.srcElement;
  while (target.nodeName !== 'LI') {
    target = target.parentElement;
  }

  var parent = target.parentElement;
  var chartId = parseInt(parent.id);
  var chart = Chart.instances[chartId];
  var index = Array.prototype.slice.call(parent.children).indexOf(target);
  var meta = chart.getDatasetMeta(0);
  var item = meta.data[index];

  chart.options.animation.duration = 400;
  // Run chart.update() to "reset" the chart and then add outerRadius after.
  chart.update();
  item._model.outerRadius += 5;
}

function bytesToSize(bytes) {
  var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  if (bytes === 0) {return 'n/a';}
  var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
  if (i === 0) {return `${bytes} ${sizes[i]}`;}
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
}

function formatNumber(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// function displayLabelUnit(TooltipItem, object) {
//   let labelName = object.labels[TooltipItem.index];
//   let dataset = object.datasets[0];
//   if (dataset.name === "nfiles"){
//     return `${labelName}: ${formatNumber(dataset.data[TooltipItem.index])} files`;
//   }
//   else if (dataset.name === "storage"){
//     return `${labelName}: ${bytesToSize(dataset.data[TooltipItem.index])}`;
//   }
//   else {
//     return `${labelName}: ${formatNumber(dataset.data[TooltipItem.index])}`;
//   }
// }



function createPie(data, ctx, colors){
  while (colors.length < data.labels.length){
    colors = colors.concat(colors);
  }
  let pie = new Chart(ctx, {
    type: "pie",
    data: {
        labels: data.labels,
        datasets: [{
            data: data.data,
            backgroundColor: colors.slice(0, data.labels.length),
            borderColor: colors.slice(0, data.labels.length),
            borderAlign: "center",
            hoverBorderWidth: 15,
            // hoverBorderWidth: [20, 20, 20, 20], // Hacky way to ensure that the enlargement at click is not outside border
            name: data.title
        }],
    },
    plugins: [ChartDataLabels],
    options: {
        plugins: {
          datalabels: {
            font: {
              size: 16,
              // weight: 'bold'
            },
            position: 'top',
            align: 'end',
            offset: 1.2,
            formatter: displayAsPercentage,
            color: '#fff',
            // anchor: 'end'
          }
        },
      legend: {
        position: 'top',
        align: 'end',
        display: false,
      },
      legendCallback: unorderedListLegend,
      tooltips: {
        events: ["mousemove"],
        enabled: true,
        backgroundColor: "white",
        displayColors: false,
        bodyFontSize: 16,
        bodyFontStyle: "bold",
        xPadding: 8,
        yPadding: 8,
        callbacks: {
          labelTextColor: (tooltipItem, chart) => {
            var dataset = chart.config.data.datasets[tooltipItem.datasetIndex];
            return dataset.backgroundColor[tooltipItem.index];
          },
          label: displayLabelUnit
        },
      },
      responsive: true,
      aspectRatio: 1,
      maintainAspectRatio: false,
      // events: []
      // events: ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove'],
      events: ['click'] // Only interactive when clicking, not hovering
    }
});
return pie;
}

function drawPies(jsonData, colors) {
  var ctx1 = document.getElementById("pie1");
  var ctx2 = document.getElementById("pie2");
  let types = jsonData.map(object => object.type);
  let nFiles = jsonData.map(object => object.n_files); // jshint ignore:line
  let totalSize = jsonData.map(object => object.total_size); // jshint ignore:line
  let pie1Data = {labels: types, data: nFiles, title: "nfiles"};
  let pie2Data = {labels: types, data: totalSize, title: "storage"};
  let pie1 = createPie(pie1Data, ctx1, colors);
  let pie2 = createPie(pie2Data, ctx2, colors);

  $("#pie1_legend").html(pie1.generateLegend());
  var pie1LegendItems = document.querySelector("#pie1_legend").getElementsByTagName('li');
  for (let j = 0; j < pie1LegendItems.length; j += 1) {
    pie1LegendItems[j].addEventListener("click", LegendClickCallback, false);
  }

  $("#pie2_legend").html(pie2.generateLegend());
  var pie2LegendItems = document.querySelector("#pie2_legend").getElementsByTagName('li');
  for (let j = 0; j < pie2LegendItems.length; j += 1) {
    pie2LegendItems[j].addEventListener("click", LegendClickCallback, false);
  }
}



let colorList = ["rgba(84, 71, 140)", 
                "rgba(44, 105, 154)",
                "rgba(4, 139, 168)",
                "rgba(13, 179, 158)",
                "rgba(22, 219, 147)",
                "rgba(131, 227, 119)",
                "rgba(185, 231, 105)",
                "rgba(239, 234, 90)",
                "rgba(241, 196, 83)"];

drawPies(jsonData, colorList);

