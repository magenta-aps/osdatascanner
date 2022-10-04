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

function getDigitLength(number) {
  return number.toString().length;
}

function bytesToKB(bytes) {
  if (bytes === 0) {return 0;}
  let KB = parseInt((bytes / Math.pow(1024, 1)).toFixed(1));
  return KB;
}

function bytesToMB(bytes) {
  if (bytes === 0) {return 0;}
  let MB = parseInt((bytes / Math.pow(1024, 2)).toFixed(1));
  return MB;
}

function bytesToNext(bytes, power) {
  if (bytes === 0) {
    var newVal = 0;
  }
  else {
    var newVal = parseInt((bytes / Math.pow(1024, power)).toFixed(1));
  }
  return newVal; 
}

function countOccurences(arr, val){
  return arr.reduce((a, v) => (v === val ? a + 1 : a), 0);
}

function binAndCount(array, binVal){
  let max = Math.max.apply(Math, array);
  // console.log(max/20)
  let binSize = Math.round(max*(binVal/100));
  let roundNumber = Math.pow(10, getDigitLength(binSize)-1);
  binSize = Math.round(binSize/roundNumber)*roundNumber;
  let nBins = Math.ceil(max/binSize);
  if (Number.isInteger(max/binSize)){
    nBins++;
  }

  let counts = Array(nBins).fill(0);
  for (let i = 0; i < array.length; i++ ){
    let index = Math.floor(array[i]/binSize);
    counts[index]++;
  }
  return [counts, binSize];
}

function getData(dataArray, granularity=16){
  const power = 1;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  console.log(dataArray.map((value) => bytesToNext(value, power)));
  let size = sizes[power];
  console.log(size);

  dataArray.sort(function(a,b) {
    return a-b;
  });
  let converted = dataArray.map(byte => bytesToKB(byte));
  let [counts, binSize] = binAndCount(converted, 4);
  let nLarge = counts.filter((val)=>val>converted.length*0.05).length;
  // console.log(nLarge)

  let nBins = counts.length;
  
  let labels = [];
  for (let i = 0; i<nBins; i++){
    labels.push(binSize*i+(binSize/2));
  }
  let points = labels.map((c, i) => ({x: c, y: counts[i]}));
  return [points, binSize];
}

function drawBars(jsonData){
  jsonData.forEach((dataset, i) => {
    let ctx = document.getElementById("bar"+(i+1).toString());
    let [data, binSize] = getData(dataset.sizes);
    let title = dataset.type.charAt(0).toUpperCase() + dataset.type.slice(1);
    createBars(data, ctx, title, binSize);
  })
}

function createBars(data, ctx, titleText, binSize){
  new Chart(ctx, {
    type: 'bar',
    data: {
      datasets: [{
        data: data,
        backgroundColor: "rgba(100, 44, 145, 0.8)",
        barPercentage: 1, 
        categoryPercentage: 1
      }]
    },
    options: {
      scales: {
        x: {
            type: 'linear',
            offset: false,
            grid: {
              offset: false
            },
            ticks: {
              stepSize: binSize,
              color: 'black',
              font: {
                size: 13
              }
            },
            title: {
              display: true,
              text: 'KB',
              font: {
                  size: 16
              },
              color: 'black'
            }
        }, 
        y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Number of files',
              font: {
                  size: 16
              },
              color: 'black'
            },
            ticks: {
              color: 'black',
              font: {
                size: 14
              }
            }
        }
      },
      plugins: {
        legend: {
        display: false
        },
        title: {
          display: true,
          text: titleText,
          font: {
            size: 20,
          },
          color: "black",
          align: "center"
        },
        scales: {
          xAxes: [{
            ticks: {
              fontSize: 12,
              weight: 'bold'}
          }]
        },
        datalabels: {
          display: false
        },
        tooltip: {
          backgroundColor: 'white',
          borderColor: "rgba(100, 44, 145, 0.8)",
          borderWidth: 1,
          titleColor: 'black',
          titleAlign: 'center',
          bodyColor: 'black',
          displayColors: false,
          padding: 10,
          callbacks: {
            label:(tooltipItem)=>{
              let start = parseInt(tooltipItem.label) - (binSize/2);
              let end = parseInt(tooltipItem.label) + (binSize/2);
                return `${start}-${end} KB`;},
            title:(tooltipItem) =>{
              let val = tooltipItem[0].formattedValue;
              if (val === '1'){
                return `${val} file`;
              }
              else {
                return `${val} files`;
              }
            }
          }
        }
      }
        
    },
    maintainAspectRatio: false,
    responsive: true,
  });
  
}
