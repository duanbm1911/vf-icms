$.ajax({
	url: '/api/inventory/dashboard-04',
	dataType: 'json',
	type: 'GET',
	success: function (data) {
		var chart = new CanvasJS.Chart("chartContainer-04", {
			animationEnabled: true,
			theme: "light2",
			exportEnabled: true,
			axisY: {
				title: "Device",
				suffix: ""
			},
			data: [{
				type: "line",
				indexLabelFontSize: 16,
				dataPoints: data.data
			}]
		});
		chart.render();
	}
})