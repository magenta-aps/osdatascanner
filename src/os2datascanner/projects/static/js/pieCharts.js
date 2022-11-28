/* exported drawPies */

function makePieChart(labels, data, colors, chartElement) {
  const pieChart = new Chart(chartElement, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors,
        hoverBackgroundColor: colors,
        borderWidth: 0,
        borderAlign: 'center',
        //Put hoverBorderWidth on - this gives the canvas a small margin, so it doesn't 'cut off' when our 'click-highlight' function
        // (sensitivityLegendClickCallback) is called. (the hover is not used, as the option: events is set to 0 ( events: [] ))
        // hoverBorderWidth: 20
      }]

    },
    plugins: [
      {
        beforeInit: function(chart) {
          const ul = document.createElement('ul');
          ul.setAttribute('class', 'pie_legend_list');
          for (let i=0; i<chart.data.labels.length; i++){
              ul.innerHTML += `
              <li>
              <span class="bullet" style="color:${chart.data.datasets[0].backgroundColor[i]}">&#8226;</span>
              </span>
              ${ chart.data.labels[i]}
              </li>
              `;  
              }
          return document.getElementById(chart.canvas.id.replace("chart", "legend")).appendChild(ul);
        }
      },
    ],
    options: {
      tooltips: {
        enabled: false,
      },
      // events: [],
      plugins: {
        legend: {
          display: false,
        },
      tooltip: {
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        borderWidth: 1,
        titleAlign: 'center',
        bodyAlign: 'center',
        bodyColor: 'black',
        titleColor: 'black',
        displayColors: false,
        callbacks: {
          label:(tooltipItem)=>{
            const val = tooltipItem.raw;
              if (val === 1){
                return val.toString().concat(" ", "resultat");
              }   
              else {
                return val.toString().concat(" ", "resultater");
              }
            },
          title:(tooltipItem)=>{
              const label = tooltipItem[0].label;
              return `${label}:`;
          },
        }
      },
      responsive: true,
      aspectRatio: 1,
      maintainAspectRatio: false
      }
    }
  });
  return pieChart;
}

function drawPies(sensitivities, sourceTypes, handledMatchesStatus) {
  //
  // Pie Chart start
  //
  //
  //
  //
  //
  // Creating sensitivites pie chart

  var sensitivitiesPieChartCtx = document.querySelector("#pie_chart_sensitivity").getContext('2d');

  const sensitivitiesPieChart = makePieChart(
    getDatasetLabels(sensitivities, 0, 1),
    getDatasetData(sensitivities, 1),
    colorData(sensitivities, 1, ['#e24e4e', '#ffab00', '#fed149', '#21759c']),
    sensitivitiesPieChartCtx
  );

  charts.push(sensitivitiesPieChart);

  // Creating datasources pie chart
  var dataSourcesPieChartCtx = document.querySelector("#pie_chart_datasources").getContext('2d');

  var dataSourcesPieChart = makePieChart(
    getDatasetLabels(sourceTypes, 0, 1),
    getDatasetData(sourceTypes, 1),
    colorData(sourceTypes, 1, ['#fed149', '#5ca4cd', '#21759c', '#00496e']),
    dataSourcesPieChartCtx
  );

  charts.push(dataSourcesPieChart);

  // Creating resolution_status pie chart
  var resolutionStatusPieChartCtx = document.querySelector("#pie_chart_resolution_status").getContext('2d');

  // sort the handledMatchesStatus the way we like it!
  handledMatchesStatus = [3, 2, 1, 4, 0].map(i => handledMatchesStatus[i]);

  var resolutionStatusPieChart = makePieChart(
    getDatasetLabels(handledMatchesStatus, 1, 2),
    getDatasetData(handledMatchesStatus, 2),
    colorData(handledMatchesStatus, 2, ['#80ab82', '#a2e774', '#35bd57', '#1b512d', '#7e4672']),
    resolutionStatusPieChartCtx
  );

  charts.push(resolutionStatusPieChart);

  function colorData(dataset, dataIndex, colorList) {
    return findRelevantData(dataset, dataIndex).map(i => colorList[i]);
  }

  function getDatasetLabels(dataset, labelIndex, dataIndex) {
    let relevantIndices = findRelevantData(dataset, dataIndex);
    let relevantLabels = [];
    for (let index of relevantIndices) {
      relevantLabels.push(dataset[index][labelIndex]);
    }
    return relevantLabels;
  }

  function getDatasetData(dataset, dataIndex) {
    let relevantIndices = findRelevantData(dataset, dataIndex);
    let relevantData = [];
    for (let index of relevantIndices) {
      relevantData.push(dataset[index][dataIndex]);
    }
    return relevantData;
  }

  function findRelevantData(dataset, dataIndex) {
    let relevantIndices = [];
    for (let i = 0; i < dataset.length; i++) {
      if (dataset[i][dataIndex] > 0) {
        relevantIndices.push(i);
      }
    }
    return relevantIndices;
  }

}
