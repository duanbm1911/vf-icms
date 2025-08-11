var chart = new CanvasJS.Chart("chartContainer-05", {
		animationEnabled: true,
		exportEnabled: true,
		theme: "light1", // "light1", "light2", "dark1", "dark2"
		axisY: {
			// title: "Số lượng thiết bị",
			suffix: "Thiết bị"
		},
		// axisX: {
		// 	title: "Countries"
		// },
		data: [{
			type: "column",
	        	indexLabelPlacement: "outside",
			yValueFormatString: "",
			dataPoints: [
				{ label: "DC/DR", y: 10 },	
				{ label: "Branch", y: 40 },	
				{ label: "HO-89LH", y: 5 },
				{ label: "HO-VHT", y: 2 },	
				{ label: "HO-VAT", y: 2 }
			]
		}]
	});
	chart.render();

