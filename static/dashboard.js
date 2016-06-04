
    
    // Create canvas elements to add to empty div.
    var canvas_tag = '<canvas id="donutChart" width = "320px" height = "320px">';
    var bar_canvas_tag = '<canvas id="barChart" width="900px" height="300px">';
    var line_canvas_tag = '<canvas id="lineChart" width="900px" height="300px">';
    var activity_line_canvas_tag = '<canvas id="activityLineChart" width="900px" height="300px">';
    var avg_line_canvas_tag = '<canvas id="avgLineChart" width="900px" height="275px">';
    var all_time_donut_canvas_tag = '<canvas id="allTimeDonutChart" width = "200px" height = "200px">';

    var options = {
      responsive: true,
      maintainAspectRatio: false
    };
    

    // Create insom_type donut chart. 
    function drawDonutChart(results) {

        $("#donutChart").remove();
        $("#canvas").append(canvas_tag);
        
        var ctx_donut = $("#donutChart").get(0).getContext("2d");
        var myDonutChart = new Chart(ctx_donut).Doughnut(results.donut_chart.insom_type, options);
        $('#donutLegend').html(myDonutChart.generateLegend());
    }



    // Create hours_sleep bar chart. 
    function drawBarChart(results) {

        $("#barChart").remove();
        $("#barCanvas").append(bar_canvas_tag);

        var ctx_bar = $("#barChart").get(0).getContext("2d");
        var myBarChart = new Chart(ctx_bar).Bar(results.bar_chart, options);
    }



    // Create stress_level vs. insomnia_severity line chart. 
    function drawLineChart(results) {

        $("#lineChart").remove();
        $("#lineCanvas").append(line_canvas_tag);

        var ctx_line = $("#lineChart").get(0).getContext("2d");
        var myLineChart = new Chart(ctx_line).Line(results.line_chart, options);
        $("#lineLegend").html(myLineChart.generateLegend());
    }



    // Create activity_level vs. insomnia_severity line chart. 
    function drawActivityLineChart(results) {

        $("#activityLineChart").remove();
        $("#activityLineCanvas").append(activity_line_canvas_tag);

        var ctx_line = $("#activityLineChart").get(0).getContext("2d");
        var myActivityLineChart = new Chart(ctx_line).Line(results.activity_line_chart, options);
        $("#activityLineLegend").html(myActivityLineChart.generateLegend());
    }



    // Create average insomnia_severity over time line chart. 
    function drawAvgLineChart(results) {

        $("#avgLineChart").remove();
        $("#avgLineCanvas").append(avg_line_canvas_tag);

        var ctx_line = $("#avgLineChart").get(0).getContext("2d");
        var myAvgLineChart = new Chart(ctx_line).Line(results.avg_line_chart, options);
    }



    // Create all-time insom_type donut chart. 
    function drawAllTimeDonutChart(results) {

        $("#allTimeDonutChart").remove();
        $("#allTimeDonutCanvas").append(all_time_donut_canvas_tag);
        
        var ctx_donut = $("#allTimeDonutChart").get(0).getContext("2d");
        var myAllTimeDonutChart = new Chart(ctx_donut).Doughnut(results.all_time_donut_chart.insom_type, options);
        $('#allTimeDonutLegend').html(myAllTimeDonutChart.generateLegend());
    }



    // Add textual data insights. 
    function addDataInsights(results) {

            $("#avg_sleep").empty();
            $("#median_sleep").empty();
            $("#avg_insomnia").empty();
            $("#median_insomnia").empty();
            $("#most_frequent_type").empty();
            $("#avg_stress").empty();
            $("#median_stress").empty();
            $("#avg_activity").empty();
            $("#median_activity").empty();
            $("#insom_factor").empty();
            $("#all_time_most_frequent_type").empty();

            var avgSleep = results.avg_median.avg_sleep;
            $("#avg_sleep").append(avgSleep);
            var medianSleep = results.avg_median.median_sleep;
            $("#median_sleep").append(medianSleep);
            var avgInsomnia = results.avg_median.avg_insomnia;
            $("#avg_insomnia").append(avgInsomnia);
            var medianInsomnia = results.avg_median.median_insomnia;
            $("#median_insomnia").append(medianInsomnia);
            var mostFrequentType = results.donut_chart.most_frequent_type;
            $("#most_frequent_type").append(mostFrequentType);
            var avgStress = results.avg_median.avg_stress;
            $("#avg_stress").append(avgStress);
            var medianStress = results.avg_median.median_stress;
            $("#median_stress").append(medianStress);
            var avgActivity = results.avg_median.avg_activity;
            $("#avg_activity").append(avgActivity);
            var medianActivity = results.avg_median.median_activity;
            $("#median_activity").append(medianActivity);
            var insomFactor = results.avg_median.insom_factor;
            $("#insom_factor").append(insomFactor);
            var allTimeMostFrequentType = results.all_time_donut_chart.all_time_most_frequent_type;
            $("#all_time_most_frequent_type").append(allTimeMostFrequentType);
    }



    // Create all charts & insights.  
    function createCharts(results) {
        drawDonutChart(results);
        drawBarChart(results);
        drawLineChart(results);
        drawActivityLineChart(results);
        drawAvgLineChart(results);
        drawAllTimeDonutChart(results);
        addDataInsights(results);
    }
    

    // WAY TO CONDENSE THESE 2 FUNCTIONS? 
    // Get user-submitted dates, pass to createCharts. 
    function getDateRange(evt) {
        // if event is this type of event, prevent default. 
        evt.preventDefault();

        var formInputs = {
            "start_date": $("#date-range input[name=start_date]").val()
        };

        $.get('/insom-types.json',
            formInputs,
            createCharts);
    }


    // Get default dates, pass to createCharts.
    function getDefaultDateRange(evt) {

        var formInputs = {
            "start_date": $("#date-range input[name=start_date]").val()
        };

        $.get('/insom-types.json',
            formInputs,
            createCharts);
    }


    //On page load, create charts with default start_date. 
    $( document ).ready(getDefaultDateRange);
    //On submit, create charts with user-selected start_date. 
    $("#date-range").on("submit", getDateRange);
    //On tab toggle, create charts with default date range. 
    $('a[data-toggle="tab"]').on('shown.bs.tab', getDateRange);




