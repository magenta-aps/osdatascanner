import jsonData from './magenta_data.json' assert {type: 'json'} // jshint ignore:line

// let colorList = ["rgba(84, 71, 140)", 
//                 "rgba(44, 105, 154)",
//                 "rgba(4, 139, 168)",
//                 "rgba(13, 179, 158)",
//                 "rgba(22, 219, 147)",
//                 "rgba(131, 227, 119)",
//                 "rgba(185, 231, 105)",
//                 "rgba(239, 234, 90)",
//                 "rgba(241, 196, 83)"];

drawBars(jsonData);

function getData(dataArray, binSize=50000){
  dataArray.sort(function(a,b) {
    return a-b;
  });
  
  let max = Math.max.apply(Math, dataArray);
  let nBins = Math.ceil(max/binSize);

  let counts = Array(nBins).fill(0);
  for (let i = 0; i < dataArray.length; i++ ){
    let index = Math.floor(dataArray[i]/binSize);
    counts[index]++;
  }
  let labels = []
  for (let i = 0; i<nBins; i++){
    labels.push((binSize*i).toString() + '-' + (binSize*(i+1)).toString());
  }
  return {counts: counts, labels: labels};
}

function drawBars(jsonData){
  jsonData.forEach((dataset, i) => {
    let ctx = document.getElementById("bar"+(i+1).toString());
    let data = getData(dataset.sizes, 25000);
    data.name = dataset.type;
    // console.log(data)
    createBars(data, ctx);
  });
}

function createBars(data, ctx){
  Chart.defaults.global.defaultFontFamily = "sans-serif";
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.labels,
      datasets: [{
        label: data.type,
        data: data.counts,
        backgroundColor: "rgba(100, 44, 145, 0.8)",
        barPercentage: 1.01, 
        categoryPercentage: 1
      }]
    },
    options: {
      legend: {
        display: false
      },
      title: {
        display: true,
        // Capitalize the first letter
        text: data.name.charAt(0).toUpperCase() + data.name.slice(1),
        fontSize: 20,
        fontColor: 'rgba( 28, 26, 25 )' 
      },
      scales: {
        xAxes: [{
          ticks: {fontSize: 12}
        }]
      },
      plugins: {
        datalabels: {
          display: false
        },
      },
    },
    maintainAspectRatio: false,
    responsive: true,
    // aspectRatio: 3
  });
}