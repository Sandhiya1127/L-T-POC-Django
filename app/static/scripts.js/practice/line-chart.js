/*
<div id="peoples_activity_line_chart"></div>
<input type="date" onchange="load_line_chart_query(this)" />
<button onclick="load_line_chart()">Generate</button>
*/
function load_line_chart(selectedDate = null) {
  let apiUrl = "https://1dc1-60-243-70-152.ngrok-free.app/workforce/idle-data/";

  if (selectedDate) {
    apiUrl += `?idle_date=${selectedDate}`;
  }

  fetch(apiUrl, {
    headers: {
      "ngrok-skip-browser-warning": "true",
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      const chartData = [];
      const points = [];

      for (const time in data) {
        if (data.hasOwnProperty(time)) {
          const [
            labour_count,
            idle_status,
            group_event,
            date,
            no_helmet,
            image_url,
          ] = data[time];

          chartData.push({
            x: time,
            y: labour_count,
            idle: idle_status,
            group: group_event,
            image: image_url,
          });

          let markerColor = "#4682b4"; // Default color
          let labelText = "Active";
          if (idle_status === "true") {
            markerColor = "#e89c0c";
            labelText = "Idle";
          }
          if (group_event === "true") {
            markerColor = "#00897B";
            labelText = "Group Talking";
          }

          points.push({
            x: time,
            y: labour_count,
            marker: {
              size: 5,
              fillColor: markerColor,
              strokeColor: markerColor,
            },
            label: {
              borderColor: markerColor,
              style: { color: "#fff", background: markerColor },
              text: labelText,
            },
          });
        }
      }

      // ✅ Pass the data to ApexCharts
      apex_lineChart("#workforce_chart", chartData, {
        // title: "Workforce Activity",
        annotations: { points: points },
      });
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}
