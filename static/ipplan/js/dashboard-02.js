$.ajax({
	url: '/api/ipplan/dashboard-02',
	dataType: 'json',
	type: 'GET',
	success: function (data) {
		console.log(data)
		var chart = new CanvasJS.Chart("chartContainer-02", {
			animationEnabled: true,
			theme: "light2", // "light1", "light2", "dark1", "dark2"
			exportEnabled: true,
			axisY: {
				title: "Subnet group",
				suffix: ""
			},
			axisX: {
				title: ""
			},
			data: [{
				type: "pie",
				yValueFormatString: "",
				dataPoints: data.data
			}]
		});
		chart.render();
	}
})


