import jsonData from './data.json' assert {type: 'json'} // jshint ignore:line

function displayAsPercentage(value, ctx) {
  let dataArr = ctx.chart.data.datasets[0].data;
  let sum = dataArr.reduce(function (total, frac) { return total + frac; });
  var percentage = Math.round(value * 100 / sum) + "%";
  return value ? percentage : '';
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

// Doesnt work - leftovers from when we used ChartJS 2. 
// Legend creation is more automatic with ChartJS 3,
// but that means that this callback is not straight forward. 

// const LegendClickCallback = function (event, legendItem, legend) {
//   console.log(legendItem)
//   console.log(legend)
//   event = event || window.event;

//   var target = event.native.target|| event.srcElement;
//   console.log(target)

//   // while (target.nodeName !== 'LI') {
//     target = target.parentElement;
//   // }

//   var parent = target.parentElement;
//   var chartId = parseInt(parent.id);
//   var chart = Chart.instances[chartId];
//   var index = Array.prototype.slice.call(parent.children).indexOf(target);
//   var meta = chart.getDatasetMeta(0);
//   var item = meta.data[index];

//   chart.options.animation.duration = 400;
//   // Run chart.update() to "reset" the chart and then add outerRadius after.
//   chart.update();
//   item._model.outerRadius += 5;
// }

function createPie(data, htmlElements, colors){
  let [ctx, pieCanvasID] = htmlElements;
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
    plugins: [
      ChartDataLabels,
      {
        beforeInit: function(chart) {
        if (chart.canvas.id === pieCanvasID) {
          const ul = document.createElement('ul');
          ul.setAttribute('class', 'chart-legend');
          for (let i=0; i<chart.data.labels.length; i++){
            ul.innerHTML += `
              <li>
              <span class="bullet" style="color:${chart.data.datasets[0].backgroundColor[i]}">&#8226;</span>
              </span>
              ${ displayLabelUnit(i, chart.data) }
              </li>
              `;
            }
          return document.getElementById(pieCanvasID+"_legend").appendChild(ul);
          }
          return;
        }
      },
    ],
    options: {
        plugins: {
          datalabels: {
            font: {
              size: 16,
              family: 'Arial'
              // weight: 'bold'
            },
            position: 'top',
            align: 'end',
            offset: 1.2,
            formatter: displayAsPercentage,
            color: '#fff',
          },
          legend: {
            display:false,
            // paddingLeft: 10,
            position: 'right',
            labels: {
              boxWidth: 7,
              boxHeight: 7,
              usePointStyle: true,
              font: {
                size: 16
              },
            }
          },
        },
      responsive: true,
      aspectRatio: 1,
      maintainAspectRatio: false,
      events: ['click']
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
  createPie(pie1Data, [ctx1, "pie1"], colors);
  createPie(pie2Data, [ctx2, "pie2"], colors);

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

