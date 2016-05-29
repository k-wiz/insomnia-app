
    
    // Create canvas elements to add to empty div.
    var canvas_tag = '<canvas id="donutChart">';
    var bar_canvas_tag = '<canvas id="barChart">';
    var line_canvas_tag = '<canvas id="lineChart">';
    var activity_line_canvas_tag = '<canvas id="activityLineChart">';
    // var bedtime_bar_canvas_tag = '<canvas id="bedtimeBarChart"'
    var avg_line_canvas_tag = '<canvas id="avgLineChart">';

    var options = {
      responsive: true
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



    // Create bedtime bar chart. 
    // function drawBedtimeBarChart(results) {

    //     $("#bedtimeBarChart").remove()
    //     $("#bedtimeBarCanvas").append(bedtime_bar_canvas_tag)

    //     var ctx_bar = $("#bedtimeBarChart").get(0).getContext("2d");
    //     var myBedtimeBarChart = new Chart(ctx_bar).Bar(results.bedtime_bar_chart, options);

    // }



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
        // $("#avgLineLegend").html(myAvgLineChart.generateLegend());
    }


    // Add textual data insights. 
    function addDataInsights(results) {

            $("#avg_sleep").empty();
            $("#median_sleep").empty();
            $("#avg_insomnia").empty();
            $("#median_insomnia").empty();
            $("#most_frequent_type").empty();
            $("#insom_factor").empty();

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
            var insomFactor = results.avg_median.insom_factor;
            $("#insom_factor").append(insomFactor);
    }



    // Create all charts & insights.  
    function createCharts(results) {
        drawDonutChart(results);
        drawBarChart(results);
        // drawBedtimeBarChart(results);
        drawLineChart(results);
        drawActivityLineChart(results);
        drawAvgLineChart(results);
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



