$.ajax({
	url: '/api/ipplan/dashboard-01',
	dataType: 'json',
	type: 'GET',
	success: function (data) {
		var chart = new CanvasJS.Chart("chartContainer-01", {
			animationEnabled: true,
			theme: "light2", // "light1", "light2", "dark1", "dark2"
			exportEnabled: true,
			axisY: {
				title: "Location",
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




