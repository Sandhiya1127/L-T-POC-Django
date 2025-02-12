// (function () {
//     // Use the global variable set in the template.
//     var cagingUrl = window.cagingUrl || "/caging/";
//     console.log("Resolved cagingUrl in external JS:", cagingUrl);
  
//     var data__deck_progress = [
//         { title: 'Rebaring', ranges: [100], measures: [40, 50], markers: [0], url: 'rebaring.html' },
//         // For "Caging", use the resolved URL.
//         { title: 'Caging', ranges: [100], measures: [30, 70], markers: [0], url: cagingUrl },
//         // For "Molding", if no URL is desired, assign a fallback.
//         { title: 'Molding', ranges: [100], measures: [60, 70], markers: [0], url: "#" }
//     ];
  
//     function d3Bullet(selector, data) {
//         var container = d3.select(selector);
//         container.selectAll('*').remove(); // Clear previous chart
  
//         var chart = d3.bullet().width(500).height(50);
  
//         var svg = container.selectAll("svg")
//         .data(data)
//         .enter()
//         .append("svg")
//         .attr("class", "bullet")
//         .attr("width", 600)
//         .attr("height", 80)
//         .style("cursor", d => (d.url && d.url !== "#" ? "pointer" : "default"))
//         .on("click", function (event, d) {
//             console.log("🔍 Clicked Data:", d);
//             console.log("🔍 Redirecting to:", d.url);
//             if (d.url && d.url !== "undefined" && d.url !== "#") {
//                 window.location.href = d.url;
//             } else {
//                 console.error("🚨 ERROR: URL is undefined or invalid for", d.title);
//             }
//         });

            
//             // .on("click", function (event, d) {
//             //     console.log("🔍 Clicked Data:", d);
//             //     console.log("🔍 Redirecting to:", d.url);
//             //     // If URL is missing, try to use the global variable for Caging
//             //     var url = d.url;
//             //     if (!url || url === "undefined") {
//             //         if (d.title === "Caging") {
//             //             url = window.cagingUrl || "/caging/";
//             //         }
//             //     }
//             //     if (url && url !== "#" && url !== "undefined") {
//             //         window.location.href = url;
//             //     } else {
//             //         console.error("🚨 ERROR: No valid URL for", d.title);
//             //     }
//             // });
  
//         svg.append("g")
//             .attr("transform", "translate(10,10)")
//             .each(function (d) {
//                 d3.select(this).call(chart);
//             });

//     //      // Ensure Caging is clickable
//     // svg.filter(d => d.title === "Caging")
//     //     .style("cursor", "pointer")
//     //     .on("click", function (event, d) {
//     //         console.log("Redirecting to:", d.url);
//     //         window.location.href = d.url;
//     //     });

//     // svg.selectAll("rect")
//     //     .style("cursor", d => d.url ? "pointer" : "default")
//     //     .on("click", function (event, d) {
//     //         if (d.url) {
//     //             console.log("Redirecting to:", d.url);
//     //             window.location.href = d.url;
//     //         }
//     //     });
// // }
//     }
  
//     // Render the bullet chart using the defined data.
//     d3Bullet('.bullet-chart-container', data__deck_progress);
  
//     // ... (the rest of your functions: playback_refresh, load_line_chart, etc.)
//   })();
  
(function () {
    // Use the global variable set in the template.
    var cagingUrl = window.cagingUrl || "/caging/";
    console.log("Resolved cagingUrl in external JS:", cagingUrl);
  
    var data__deck_progress = [
        { title: 'Rebaring', ranges: [100], measures: [40, 50], markers: [0], url: 'rebaring.html' },
        { title: 'Caging', ranges: [100], measures: [30, 70], markers: [0], url: cagingUrl },
        { title: 'Molding', ranges: [100], measures: [60, 70], markers: [0], url: "#" }
    ];
  
    function d3Bullet(selector, data) {
        var container = d3.select(selector);
        container.selectAll('*').remove(); // Clear previous chart
  
        var chart = d3.bullet().width(700).height(50);
  
        // Create SVG elements (one per data item)
        var svg = container.selectAll("svg")
            .data(data)
            .enter()
            .append("svg")
            .attr("class", "bullet")
            .attr("width", 700)
            .attr("height", 80)
            // Set cursor style if URL is valid.
            .style("cursor", d => (d.url && d.url !== "#" ? "pointer" : "default"));

            svg.append("text")
        .attr("x", 5) // Left position for text
        .attr("y", 40) // Align vertically with bars
        .attr("dy", ".35em") // Fine-tune alignment
        .attr("text-anchor", "start") // Left-align text
        .style("font-size", "14px") // Adjust font size
        .style("font-weight", "bold")
        .style("fill", "#333") // Ensure visibility
        .text(d => d.title);

    // Shift bullet bars **to the right** to make space for titles
    svg.append("g")
        .attr("transform", "translate(70,10)") // Move bars right after titles
        .each(function (d) {
            d3.select(this).call(chart);
        });


            svg.filter(d => d.title === "Caging")
            .style("cursor", "pointer")
            .on("click", function (event, d) {
                var redirectUrl = d.url;
                if (!redirectUrl || redirectUrl === "undefined") {
                    redirectUrl = window.cagingUrl || "/caging/";
                }
                console.log("Redirecting to:", redirectUrl);
                window.location.href = redirectUrl;
            });
          
        // svg.append("g")
        //     .attr("transform", "translate(10,10)")
        //     .each(function (d) {
        //         d3.select(this).call(chart);
        //     });
  
        svg.append("rect")
            .attr("width", 800)
            .attr("height", 90)
            .style("fill", "transparent")
            .style("pointer-events", "all")
            .on("click", function (event, d) {
                console.log("Transparent overlay clicked, data:", d);
                console.log("Redirecting to:", d.url);
                if (d.url && d.url !== "undefined" && d.url !== "#") {
                    window.location.href = d.url;
                } else {
                    console.error("🚨 ERROR: URL is undefined or invalid for", d.title);
                }
            });
    }
  
    d3Bullet('.bullet-chart-container', data__deck_progress);
  
  })();
  