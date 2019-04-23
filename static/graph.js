$(document).ready(function() {
$(chart1_id).highcharts({
		// Endrer fargen paa toggler
		legend: {
            itemStyle: {
                color: 'black',
                fontWeight: 'bold'
            }
        },


		credits: {
        enabled: false
    	},
		chart: chart1,
		title: title1,
		xAxis: xAxis1,
		yAxis: yAxis1,
		series: series1

});
$(chart2_id).highcharts({
		// Endrer fargen paa toggler
		legend: {
            itemStyle: {
                color: 'black',
                fontWeight: 'bold'
            }
        },


		credits: {
        enabled: false
    	},
		chart: chart2,
		title: title2,
		xAxis: xAxis2,
		yAxis: yAxis2,
		series: series2
});
$(chart_turb_id).highcharts({
		// Endrer fargen paa toggler
		legend: {
            itemStyle: {
                color: 'black',
                fontWeight: 'bold'
            }
        },

		credits: {
        enabled: false
    	},
		chart: chart_turb,
		title: title_turb,
		xAxis: xAxis_turb,
		yAxis: yAxis_turb,
		series: series_turb
});
$(chart_kond_id).highcharts({
		// Endrer fargen paa toggler
		legend: {
            itemStyle: {
                color: 'black',
                fontWeight: 'bold'
            }
        },


		credits: {
        enabled: false
    	},
		chart: chart_kond,
		title: title_kond,
		xAxis: xAxis_kond,
		yAxis: yAxis_kond,
		series: series_kond
});
});
