var chart = new CanvasJS.Chart("chartContainer-04", {
        theme: "light2", // "light1", "light2", "dark1", "dark2"
        exportEnabled: true,
        animationEnabled: true,
        data: [{
            type: "pie",
            startAngle: 25,
            toolTipContent: "<b>{label}</b>: {y}",
            showInLegend: "true",
            legendText: "{label}",
            indexLabelFontSize: 16,
            indexLabel: "{label} - {y}",
            dataPoints: [
                { y: 51, label: "DC/DR" },
                { y: 27, label: "Branch" },
                { y: 10, label: "HO-VHT" },
                { y: 5, label: "HO-VAT" },
                { y: 4, label: "HN-MNT" }
            ]
        }]
    });
    chart.render();

