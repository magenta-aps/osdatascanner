function bytesToSize(bytes) {
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
    if (bytes === 0) {return "n/a";}
    const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
    if (i === 0) {return `${bytes} ${sizes[i]}`;}
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
}

function unorderedListLegend(data, colors, chart) {
    let text = [`<ul id="${chart.id}" class="pie_legend_list">`];

    const totalValue = data.data.reduce((sum, obj) => sum + (obj || 0)); // Get the total of all non-zero data points

    for (let i = 0; i < data.data.length; i++) {
      const value = data.data[i];
      const label = data.labels[i].charAt(0).toUpperCase() + data.labels[i].slice(1);
      const backgroundColor = colors[i];

      const percentage = value ? ((value / totalValue) * 100).toFixed(2) + "%" : "0%"; // Calculate percentage based on totalValue

      if (value > 0) {
        text.push(`<li><span class="bullet" style="color:${backgroundColor}">&#8226;</span>`);
        if (label) {
            text.push(`<span class="legend-txt">${label}</span>`,
                      `<span class="data-label">${percentage}</span>`);
        }
        text.push("</li>");
      }
    }
    text.push("</ul>");
    return text.join("");
  }

function createPie(data, htmlElements, colors){ // jshint ignore:line
    let ctx = htmlElements[0];
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
                hoverBackgroundColor: colors.slice(0, data.labels.length),
                borderColor: colors.slice(0, data.labels.length),
                name: data.name,
                hoverBorderWidth:0
            }],
        },
        options: {
            plugins: {
            datalabels: {
                display: false,
            },
            legend: {
                display: false,
            },
            tooltip: {
                backgroundColor: "rgba(255, 255, 255, 0.8)",
                borderWidth: 1,
                titleAlign: "center",
                bodyAlign: "center",
                bodyColor: "black",
                titleColor: "black",
                displayColors: false,
                callbacks: {
                    label:(tooltipItem)=>{
                        const name = tooltipItem.dataset.name;
                        const val = tooltipItem.raw;
                        if (name === "storage"){
                            return bytesToSize(val);
                        }
                        else if (name === "nfiles"){
                            if (val === 1){
                                return val.toString().concat(" ", gettext("file"));
                            }
                            else {
                                return val.toString().concat(" ", gettext("files"));
                            }
                        }
                    },
                    title:(tooltipItem)=>{
                        const label = tooltipItem[0].label;
                        return `${label}:`;
                    },
                }
            },
            },
        responsive: true,
        maintainAspectRatio: false,
        }
    });
    document.getElementById(ctx.id + "_legend").innerHTML = unorderedListLegend(data, colors, pie);
    return pie;
}
