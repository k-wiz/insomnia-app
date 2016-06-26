
    // NOTE: During Phase 3 refactor, rename tags and ids more descriptive
    // and intuitive names. 

    // Create canvas elements to add to empty div.
    var canvas_tag,
        bar_canvas_tag,
        line_canvas_tag,
        activity_line_canvas_tag,
        avg_line_canvas_tag,
        all_time_donut_canvas_tag,
        options;

    canvas_tag = '<canvas id="donutChart" width = "320px" height = "320px">';
    bar_canvas_tag = '<canvas id="barChart" width="900px" height="300px">';
    line_canvas_tag = '<canvas id="lineChart" width="900px" height="300px">';
    activity_line_canvas_tag = '<canvas id="activityLineChart" width="900px" height="300px">';
    avg_line_canvas_tag = '<canvas id="avgLineChart" width="900px" height="275px">';
    all_time_donut_canvas_tag = '<canvas id="allTimeDonutChart" width = "200px" height = "200px">';

    options = {
      responsive: true,
      maintainAspectRatio: false
    };
    

    // Create insom_type donut chart. 
    function drawDonutChart(results) {

        $("#donutChart").remove();
        $("#canvas").append(canvas_tag);
        
        var ctx_donut, myDonutChart;

        ctx_donut = $("#donutChart").get(0).getContext("2d");
        myDonutChart = new Chart(ctx_donut).Doughnut(results.donut_chart.insom_type, options);
        $('#donutLegend').html(myDonutChart.generateLegend());
    }



    // Create hours_sleep bar chart. 
    function drawBarChart(results) {

        $("#barChart").remove();
        $("#barCanvas").append(bar_canvas_tag);

        var ctx_bar, myBarChart;

        ctx_bar = $("#barChart").get(0).getContext("2d");
        myBarChart = new Chart(ctx_bar).Bar(results.bar_chart, options);
    }



    // Create stress_level vs. insomnia_severity line chart. 
    function drawLineChart(results) {

        $("#lineChart").remove();
        $("#lineCanvas").append(line_canvas_tag);

        var ctx_line, myLineChart;

        ctx_line = $("#lineChart").get(0).getContext("2d");
        myLineChart = new Chart(ctx_line).Line(results.line_chart, options);
        $("#lineLegend").html(myLineChart.generateLegend());
    }



    // Create activity_level vs. insomnia_severity line chart. 
    function drawActivityLineChart(results) {

        $("#activityLineChart").remove();
        $("#activityLineCanvas").append(activity_line_canvas_tag);

        var ctx_line, myActivityLineChart;

        ctx_line = $("#activityLineChart").get(0).getContext("2d");
        myActivityLineChart = new Chart(ctx_line).Line(results.activity_line_chart, options);
        $("#activityLineLegend").html(myActivityLineChart.generateLegend());
    }



    // Create average insomnia_severity over time line chart. 
    // function drawAvgLineChart(results) {

    //     $("#avgLineChart").remove();
    //     $("#avgLineCanvas").append(avg_line_canvas_tag);

    //     var ctx_line, myAvgLineChart;

    //     ctx_line = $("#avgLineChart").get(0).getContext("2d");
    //     myAvgLineChart = new Chart(ctx_line).Line(results.avg_line_chart, options);
    // }



    // Create all-time insom_type donut chart. 
    // function drawAllTimeDonutChart(results) {

    //     $("#allTimeDonutChart").remove();
    //     $("#allTimeDonutCanvas").append(all_time_donut_canvas_tag);

    //     var ctx_donut, myAllTimeDonutChart;
        
    //     ctx_donut = $("#allTimeDonutChart").get(0).getContext("2d");
    //     myAllTimeDonutChart = new Chart(ctx_donut).Doughnut(results.all_time_donut_chart.insom_type, options);
    //     $('#allTimeDonutLegend').html(myAllTimeDonutChart.generateLegend());
    // }



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
            $("#insom_factor_insight_text").empty();
            $("#most_frequent_insom_type_text").empty();

            var avgSleep,
                medianSleep,
                avgInsomnia,
                medianInsomnia,
                mostFrequentType,
                avgStress,
                medianStress,
                avgActivity,
                medianActivity,
                insomFactor,
                allTimeMostFrequentType,
                mostFrequentInsomTypeText;

            avgSleep = results.avg_median.avg_sleep;
            $("#avg_sleep").append(avgSleep);
            medianSleep = results.avg_median.median_sleep;
            $("#median_sleep").append(medianSleep);
            avgInsomnia = results.avg_median.avg_insomnia;
            $("#avg_insomnia").append(avgInsomnia);
            medianInsomnia = results.avg_median.median_insomnia;
            $("#median_insomnia").append(medianInsomnia);
            mostFrequentType = results.donut_chart.most_frequent_type;
            $("#most_frequent_type").append(mostFrequentType);
            avgStress = results.avg_median.avg_stress;
            $("#avg_stress").append(avgStress);
            medianStress = results.avg_median.median_stress;
            $("#median_stress").append(medianStress);
            avgActivity = results.avg_median.avg_activity;
            $("#avg_activity").append(avgActivity);
            medianActivity = results.avg_median.median_activity;
            $("#median_activity").append(medianActivity);
            insomFactor = results.avg_median.insom_factor;
            $("#insom_factor").append(insomFactor);
            insomFactorText = results.avg_median.insom_factor_insight_text;
            $("#insom_factor_insight_text").append(insomFactorText);
            allTimeMostFrequentType = results.avg_median.all_time_most_frequent_type;
            $("#all_time_most_frequent_type").append(allTimeMostFrequentType);
            mostFrequentInsomTypeText = results.avg_median.most_frequent_insom_type_text;
            $("#most_frequent_insom_type_text").append(mostFrequentInsomTypeText);
    }



    // Create all charts & insights.  
    function createCharts(results) {
        drawDonutChart(results);
        drawBarChart(results);
        drawLineChart(results);
        drawActivityLineChart(results);
        // drawAvgLineChart(results);
        // drawAllTimeDonutChart(results);
        addDataInsights(results);
    }
    

    // Get user-submitted dates or default date range, pass to createCharts. 
    function getDateRange(evt) {
 
        if (evt.type == "submit") {
            evt.preventDefault();
        }

        var formInputs = {
            "start_date": $("#date-range input[name=start_date]").val()
        };

        $.get('/insom-types.json',
            formInputs,
            createCharts);
    }


    //On page load, create charts with default start_date. 
    $( document ).ready(getDateRange);

    //On submit, create charts with user-selected start_date. 
    $("#date-range").on("submit", getDateRange);

    //On tab toggle, create charts with default date range. 
    $('a[data-toggle="tab"]').on('shown.bs.tab', getDateRange);




