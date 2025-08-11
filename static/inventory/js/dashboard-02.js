$.ajax({
	url: '/api/inventory/dashboard-02',
	dataType: 'json',
	type: 'GET',
	success: function (data) {
		var chart = new CanvasJS.Chart("chartContainer-02", {
			animationEnabled: true,
			theme: "light2", // "light1", "light2", "dark1", "dark2"
			exportEnabled: true,
			axisY: {
				title: "Device",
				suffix: ""
			},
			axisX: {
				title: ""
			},
			data: [{
				type: "column",
				yValueFormatString: "",
				dataPoints: data.data
			}]
		});
		chart.render();
	}
})


