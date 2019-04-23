$(document).ready(function() {
$(chart1_id).highcharts({
		credits: {
        enabled: false
    	},
    	
		chart: chart1,
		title: title1,
		xAxis: xAxis1,
		yAxis: yAxis1,
		series: [{
        data: [29.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4],
        visible: false
    }, {
        data: [144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4, 29.9, 71.5, 106.4, 129.2]
    }]

});
});
