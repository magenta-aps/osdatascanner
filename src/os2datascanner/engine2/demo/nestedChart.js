// Loading mock data
import jsonData from './data.json' assert {type: 'json'} // jshint ignore:line

function getData(jsonData, variable){
  var labels = [];
  var global = [];
  var buckets = [];
  jsonData.forEach((entry) => {
    entry.buckets.forEach((bucket) => {
      buckets.push(bucket[variable]);
    });
    labels.push(entry.type);
    global.push(entry[variable]);
  });
  let data = {
    "labels": labels,
    "outer": global,
    "buckets": buckets
  };
  return data;
}

function getColors(){
  // Hacky solution for dynamically insetting alphas in the same base color
  let colorList = ["rgba(94, 21, 157)", 
                    "rgba(15, 162, 131)",
                    "rgba(184, 95, 13)",
                    "rgba(167, 28, 60)",
                    "rgba(82, 167, 4)",
                    "rgba(38, 70, 197)"];

  var outerLayer = [colorList[0], colorList[1]];
  var innerLayer = Array(4).fill(colorList[0]).concat(Array(4).fill(colorList[1]));

  let colors = {
    "outerLayer": outerLayer,
    "innerLayer": innerLayer,
    "hoverBorder": "rgba(2, 2, 60, 1)"
  };
  return colors;
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

function getChartData(data, colors) {
  const nBuckets = data.buckets.length / data.labels.length;
  var innerLabels = Array(nBuckets).fill();
  for (let i = 1; i <= nBuckets; i++) {
    innerLabels[i-1] = `Quartile ${i}`;
  }
  var chartData = {
    datasets: [
      { 
        label:"Outer",
        labels: data.labels,
        data: data.outer,
        sum: data.outer.reduce((a, b) => a + b, 0),
        backgroundColor: colorList.map(color => color.replace(")", ", 0.8)")),
        hoverBackgroundColor: colorList.map(color => color.replace(")", ", 1)")),
        hoverBorderColor: colors.hoverBorder
      },
      { 
        label: "Inner",
        labels: innerLabels.concat(innerLabels), //doubling because of 
        data: data.buckets,
        sum: data.buckets.reduce((a, b) => a + b, 0),
        backgroundColor: colorList.map(color => color.replace(")", ", 0.5)")),
        hoverBackgroundColor: colorList.map(color => color.replace(")", ", 1)")),
        hoverBorderColor: colors.hoverBorder
      },
    ]  
  };
  return chartData;
}

function getOptions(title, titleColor="rgba(2, 2, 60, 1)") {
  var chartOptions = {
    elements: {
      arc: {
        roundedCornersFor: 0
      },
      center: {
        minFontSize: 20,
        maxFontSize: 20,
        weight: 'bold',
        text: "something",
      }
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (context) => {
            return `${context.dataset.labels[context.dataIndex]}: ${context.formattedValue}`;
          }
        }
      },
      title: {
        display: true,
        text: title,
        color: titleColor,
        font: {
          size: 30
        }
      },
      // datalabels: {
      //   color: "rgba(241, 241, 252, 1)",
      //   formatter: (value, context) => {
      //       if (context.dataset.label !== "Outer"){
      //         return "";
      //       }
      //       else {
      //         return context.dataset.labels[context.dataIndex];
      //       }
      //   },
      //   font: {
      //     weight: "bold",
      //     size: 13
      //   },
      // }
    },
    // cutout: "50%",    
  };
  return chartOptions;
}

function drawChart(type, context, data, options) {
  var theChart = new Chart(context, {
    type: type,
    data: data,
    // plugins: [ChartDataLabels],
    options: options,
    centerText: {
      display: true,
      text: "hello"
    }
  });
  // Chart.pluginService.register({
  //   beforeDraw: function (chart) {
  //     if (chart.config.type === 'doughnut') {
  //       console.log("at BeforeDraw")
  //     }
  //   } 
  // })
  return theChart;
}
// Defining colors
// Green and blue
// const color1 = "rgba(38, 70, 197, "
// const color2 = "rgba(82, 167, 4, "

// Red-ish brown/orange-ish --> earth colors
// const color1 = "rgba(167, 28, 60, "
// const color2 = "rgba(184, 95, 13, "

// Purple and turquise 
// const color1 = "rgba(94, 21, 157, ";
// const color2 = "rgba(15, 162, 131, ";
var colors = getColors();

var data = getData(jsonData, "mean");
var ctx = document.getElementById("mean");
var chartData = getChartData(data, colors);
var chartOptions = getOptions("Analysis of mean", undefined, undefined, "hello");

drawChart("pie", ctx, chartData, chartOptions);

var data = getData(jsonData, "median");
var ctx = document.getElementById("median");
var chartData = getChartData(data, colors);
var chartOptions = getOptions("Analysis of median", undefined, undefined, "hello");

drawChart("pie", ctx, chartData, chartOptions);

