$.ajax({
	url: '/api/inventory/dashboard-07',
	dataType: 'json',
	type: 'GET',
	success: function (data) {
		var chart = new CanvasJS.Chart("chartContainer-07", {
			animationEnabled: true,
			theme: "light2",
			exportEnabled: true,
			axisX:{
				valueFormatString: "",
				crosshair: {
					enabled: true,
					snapToDataPoint: true
				}
			},
			axisY: {
				title: "Device",
				includeZero: true,
				crosshair: {
					enabled: true
				}
			},
			toolTip:{
				shared:true
			},  
			legend:{
				cursor:"pointer",
				verticalAlign: "bottom",
				horizontalAlign: "center",
				itemclick: toogleDataSeries
			},
			data: data.data
		});
		chart.render();

		function toogleDataSeries(e){
			if (typeof(e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
				e.dataSeries.visible = false;
			} else{
				e.dataSeries.visible = true;
			}
			chart.render();
		}
	}
})