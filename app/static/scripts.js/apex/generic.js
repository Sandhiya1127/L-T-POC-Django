let chart;

function apex_lineChart(querySelector, data, options) {
  const newOptions = {
    chart: {
      height: 380,
      type: "line",
      id: "workforce_chart",
      fontFamily: "Arial, sans-serif",
    },
    stroke: {
      curve: "smooth",
      width: 2, // Keep the line thickness as before
    },
    grid: {
      show: true,
      borderColor: "#E0E0E0",
      strokeDashArray: 4, // Dashed grid lines
    },
    colors: ["#4682b4"], // Old chart color (adjust if different)
    theme: {
      mode: "light", // Change to "dark" if old chart was dark
      palette: "palette1",
    },
    background: "#ffffff", // Keep background same as before
    series: [{ name: "Labour Count", data: data.map((d) => d.y) }],
    labels: data.map((d) => d.x),
    tooltip: {
      custom: function ({ dataPointIndex }) {
        const point = data[dataPointIndex];

        if (point.image) {
          return `<div style="padding:15px;">
                    <strong>Time:</strong> ${point.x}<br />
                    <strong>Labour Count:</strong> ${point.y}<br />
                    <img src="${point.image}" alt="Work Progress" 
                      style="width:200px;height:auto;margin-top:5px;border-radius:5px;box-shadow: 2px 2px 10px rgba(0,0,0,0.2);" />
                  </div>`;
        }

        return `<div style="padding:10px;">
                  <strong>Time:</strong> ${point.x}<br />
                  <strong>Labour Count:</strong> ${point.y}<br />
                </div>`;
      },
    },
    annotations: options.annotations,
    xaxis: {
      labels: {
        style: {
          fontSize: "12px",
          fontWeight: "bold",
          colors: "#333333",
        },
      },
    },
  };

  if (window.chart) {
    window.chart.updateOptions(newOptions);
    window.chart.updateSeries([{ data: data.map((d) => d.y) }]);
  } else {
    window.chart = new ApexCharts(document.querySelector(querySelector), newOptions);
    window.chart.render();
  }
}


function apex_donutChart(querySelector = '', data = {}, options = {}) {
  var data_series = [],
    data_labels = [];
  for (let key of Object.keys(data)) {
    data_series.push(data[key]);
    data_labels.push(key);
  }

  var options = {
    series: data_series, //[44, 55, 13, 33],
    chart: {
      width: 380,
      type: 'donut',
    },
    labels: data_labels,
    dataLabels: {
      enabled: false,
    },
    responsive: [
      {
        // breakpoint: 480,
        options: {
          chart: {
            width: 200,
          },
          legend: {
            show: false,
          },
        },
      },
    ],
    legend: {
      position:
        (options && options['legend'] && options['legend']['position']) ||
        'right',
      offsetY:
        (options && options['legend'] && options['legend']['offsetY']) || 10,
      height:
        (options && options['legend'] && options['legend']['height']) || 50,
      // floating: true
    },
    colors: (options && options['colors']) || ['#4682b4'],
  };

  var chart = new ApexCharts(document.querySelector(querySelector), options);
  //console.log(options);

  chart.render();
}

function apex_heatChart(
  querySelector = '',
  apiUrl = 'https://1dc1-60-243-70-152.ngrok-free.app/time_series'
) {
  // Fetch data from the API
  fetch(apiUrl, {
    headers: {
      'ngrok-skip-browser-warning': 'true',
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((apiData) => {
      // Convert the apiData object to an array of [date, values]
      const entries = Object.entries(apiData);

      // Sort the entries by date in ascending order
      entries.sort((a, b) => new Date(a[0]) - new Date(b[0]));

      // Process the sorted entries
      let seriesData = [];

      for (const [date, values] of entries) {
        let dateSeriesData = [];
        // Format data for the heatmap
        for (const [
          hour,
          value,
          labour_count,
          ,
          ,
          active_m,
          inactive_m,
        ] of values) {
          dateSeriesData.push({
            x: hour.toString(),
            y: value,
            labour_count: labour_count,
            active_m: active_m,
            inactive_m: inactive_m,
          });
        }

        // Add the formatted data to the series
        seriesData.push({
          name: date, // Use the date as the series name
          data: dateSeriesData, // Populate series data with x and y values
        });
      }
      console.log('seriesData:', seriesData);

      // Add a container for the custom tooltip
      let tooltipContainer = document.createElement('div');
      tooltipContainer.id = 'custom-tooltip';
      tooltipContainer.style.display = 'none'; // Initially hidden
      tooltipContainer.style.position = 'fixed';
      tooltipContainer.style.right = '105px'; // Positioned to the right
      tooltipContainer.style.top = '485px'; // Adjust this as needed
      tooltipContainer.style.width = '350px';
      tooltipContainer.style.backgroundColor = '#f8f9fa';
      tooltipContainer.style.border = '1px solid #dee2e6';
      tooltipContainer.style.borderRadius = '8px';
      tooltipContainer.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
      tooltipContainer.style.padding = '15px';
      tooltipContainer.style.zIndex = '1000';
      tooltipContainer.innerHTML = `
        <h5 class="title-heading">
          Summary:
          <span id="tooltip-date" class="text-secondary"></span>
        </h5>
        <p id="tooltip-content" style="text-align: justify" class="mt-4"></p>
      `;

      // Append tooltip to the body
      document.body.appendChild(tooltipContainer);

      // Chart configuration
      var options = {
        chart: {
          height: 225,
          type: 'heatmap',
          events: {
            dataPointMouseEnter: function (event, chartContext, config) {
              const hoveredData =
                  config.w.globals.series[config.seriesIndex][config.dataPointIndex];
              const hoveredHour = config.w.globals.labels[config.dataPointIndex];
              const hoveredDate = config.w.globals.seriesNames[config.seriesIndex];
          
              // Find labour_count from the series data
              const labourCount =
                  seriesData[config.seriesIndex].data[config.dataPointIndex].labour_count;
              const inactive_m =
                  seriesData[config.seriesIndex].data[config.dataPointIndex].inactive_m;
              const active_m =
                  seriesData[config.seriesIndex].data[config.dataPointIndex].active_m;
          
              // Update the content inside the summary box instead of a floating tooltip
              document.getElementById('date-summary').innerHTML = hoveredDate;
              document.getElementById('summary-content').innerHTML = `
               <h5 class="title-heading">
                  Summary:
                  <span id="tooltip-date" class="text-secondary"></span>
                </h5>
                  <strong>Time:</strong> ${hoveredHour}:00<br>
                  <strong>Idle Time and Group Event:</strong> ${inactive_m} minutes<br>
                  <strong>Inactive:</strong> ${hoveredData}%<br>
              `;
              
          
              // Ensure the summary box is visible
              document.getElementById('heatmap-summary').style.display = 'block';
          },
          dataPointMouseLeave: function (event, chartContext, config) {
            // Hide the summary box when the mouse leaves the heatmap
            document.getElementById('heatmap-summary').style.display = 'none';
        },
          
          },
        },
        colors: ['#00C853', '#FFA726', '#E65100'],
        plotOptions: {
          heatmap: {
            shadeIntensity: 1,
            radius: 0,
            useFillColorAsStroke: true,
            colorScale: {
              ranges: [
                {
                  from: 0,
                  to: 20,
                  name: 'Low',
                  color: '#00C853',
                },
                {
                  from: 21,
                  to: 40,
                  name: 'Medium',
                  color: '#FFA726',
                },
                {
                  from: 41,
                  to: 100, // Set to a high number to cover all values
                  name: 'High',
                  color: '#E65100',
                },
              ],
            },
          },
        },
        dataLabels: {
          enabled: false,
        },
        stroke: {
          width: 1,
        },
        series: seriesData, // Use the processed series data
        tooltip: {
          enabled: false, // Disable default tooltips to use custom one
        },
      };

      // Render the chart
      var chart = new ApexCharts(
        document.querySelector(querySelector),
        options
      );
      chart.render();
    })
    .catch((error) => {
      console.error('Error fetching or processing data:', error);
    });
}
