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

function getColors(color1, color2, hoverBorder="rgba(2, 2, 60, 1)"){
  // Hacky solution for dynamically insetting alphas in the same base color
  const alphaHover = "1)";
  const alphaOuter = "0.8)";
  const alphaInner = "0.5)";
  var outerLayer = [color1.concat(alphaOuter), color2.concat(alphaOuter)];
  var outerHover  = [color1.concat(alphaHover), color2.concat(alphaHover)];
  var innerLayer = Array(4).fill(color1.concat(alphaInner)).concat(Array(4).fill(color2.concat(alphaInner)));
  var innerHover = Array(4).fill(color1.concat(alphaHover)).concat(Array(4).fill(color2.concat(alphaHover)));
  let colors = {
    "outerLayer": outerLayer,
    "outerHover": outerHover,
    "innerLayer": innerLayer,
    "innerHover": innerHover,
    "hoverBorder": hoverBorder
  };
  return colors;
}

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
        backgroundColor: colors.outerLayer,
        hoverBackgroundColor: colors.outerHover,
        hoverBorderColor: colors.hoverBorder
      },
      { 
        label: "Inner",
        labels: innerLabels.concat(innerLabels),
        data: data.buckets,
        sum: data.buckets.reduce((a, b) => a + b, 0),
        backgroundColor: colors.innerLayer,
        hoverBackgroundColor: colors.innerHover,
        hoverBorderColor: colors.hoverBorder
      }]  
  };
  return chartData;
}

function getOptions(title, titleColor="rgba(2, 2, 60, 1)", legendPosition="right") {
  var chartOptions = {
    plugins: {
      legend: {
        display: true,
        position: legendPosition
      },
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
      datalabels: {
        color: "rgba(241, 241, 252, 1)",
        formatter: (value, context) => {
            if (context.dataset.label !== "Outer"){
              return "";
            }
            else {
              return context.dataset.labels[context.dataIndex];
            }
        },
        font: {
          weight: "bold",
          size: 13
        },
      }
    },
  };
  return chartOptions;
}

function drawChart(type, context, data, options) {
  var theChart = new Chart(context, {
    type: type,
    data: data,
    // options: options,
    plugins: [ChartDataLabels],
    options: options
  });
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
const color1 = "rgba(94, 21, 157, ";
const color2 = "rgba(15, 162, 131, ";
var colors = getColors(color1, color2);

var data = getData(jsonData, "mean");
var ctx = document.getElementById("mean");
var chartData = getChartData(data, colors);
var chartOptions = getOptions("Analysis of mean");

drawChart("pie", ctx, chartData, chartOptions);

var data = getData(jsonData, "median");
var ctx = document.getElementById("median");
var chartData = getChartData(data, colors);
var chartOptions = getOptions("Analysis of median");

drawChart("pie", ctx, chartData, chartOptions);



