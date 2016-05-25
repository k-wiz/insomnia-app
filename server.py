"""Insomnia App"""

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import connect_to_db, db, User, Entry
from datetime import datetime, time, date, timedelta
from sqlalchemy import func, update
from helper import *
import numpy as np
import requests
import fitbit
import os

app = Flask(__name__)
app.secret_key = "DOESNTMATTER"
app.jinja_env.undefined = StrictUndefined

###################################################################

@app.route('/')
def index():
    """Display today's entry form."""

    consumer_key = os.environ['client_id']
    consumer_secret = os.environ['client_secret']
    access_token = os.environ['access_token']
    refresh_token = os.environ['refresh_token']

    authd_client = fitbit.Fitbit(consumer_key, consumer_secret,
                             access_token=access_token, refresh_token=refresh_token)
    
    sleep_log = authd_client.sleep()



    hours_sleep = sleep_log['summary']['totalMinutesAsleep'] / 60
    


    #Alert user?


    return render_template("homepage.html", 
                                hours_sleep = hours_sleep)



##########################################################################


@app.route('/dashboard', methods=["POST"])
def dashboard():
    """Display user's dashboard."""

    # Retrieve form data.  
    user_id = 1 
    date = datetime.now()
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    minutes_asleep = int(request.form.get("hours_sleep")) * 60
    insomnia = convert_to_boolean(request.form.get("insomnia"))
    insom_type = request.form.get("insom_type")
    insom_severity = int(request.form.get("insom_severity"))
    alcohol = convert_to_boolean(request.form.get("alcohol"))
    caffeine = convert_to_boolean(request.form.get("caffeine"))
    menstruation = convert_to_boolean(request.form.get("menstruation"))
    bedtime = datetime.strptime((request.form.get("bedtime")), '%H:%M')
    stress_level = int(request.form.get("stress_level"))
    activity_level = int(request.form.get("activity_level"))


    # Create new record in db if no existing record with user_id and date;
    # otherwise, update current record. 
    create_or_update_record(user_id, date, minutes_asleep, insomnia, insom_type,
                            insom_severity, alcohol, caffeine, menstruation,
                            bedtime, stress_level, activity_level)


    # Calculate sleep insights for user with user_id. 
    start_date = first_entry(user_id)
    end_date = last_entry(user_id)
    avg_sleep = calculate_avg_sleep(user_id, start_date, end_date)
    avg_insom_severity = calculate_avg_insom_severity(user_id, start_date, end_date)
    median_sleep = calculate_median_sleep(user_id, start_date, end_date)
    median_insom_severity = calculate_median_insom_severity(user_id, start_date, end_date)
    # most_frequent_type_insomnia = (most_frequent_type(user_id, start_date, end_date))[1]


    # Pass calculated data to template
    return render_template("dashboard2.html", 
                                avg_sleep=avg_sleep,
                                median_sleep=median_sleep,
                                avg_insom_severity=avg_insom_severity,
                                median_insom_severity=median_insom_severity)


##########################################################################


@app.route('/insom-types.json')
def insom_type_data():
    """Returns a jsonified dictionary of values needed to create charts."""
 
    user_id = 1

    #REFACTOR!!! MOVE TO HELPER FUNCTION.
    default_start_date = datetime.strftime(two_weeks_before_last_entry(user_id), '%Y-%m-%d')
    start = request.args.get("start_date", default_start_date)
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = start_date + timedelta(14)

    total_days = end_date - start_date
    total_days = total_days.days + 1


    
    #Create values & labels for donutChart. 
    a = frequency_no_insomnia(user_id, start_date, end_date)
    b = frequency_early_insomnia(user_id, start_date, end_date)
    c = frequency_maintenance_insomnia(user_id, start_date, end_date)
    d = frequency_onset_insomnia(user_id, start_date, end_date)


    donut_dict = {
        'insom_type': [
            {
                "value": a, 
                "color": "#A9A9A9",
                "highlight": "#808080",
                "label": "No insomnia yay!"
            },
            {
                "value": b,
                "color": "#46BFBD",
                "highlight": "#5AD3D1",
                "label": "Early-awakening insomnia"
            },
            {
                "value": c,
                "color": "#F7464A",
                "highlight": "#FF5A5E",
                "label": "Sleep-maintenace insomnia"
            },
            {
                "value": d,
                "color": "#FDB45C",
                "highlight": "#FFC870",
                "label": "Sleep-onset insomnia"
            }
        ]
        # 'avg_sleep': avg_sleep,
        # 'median_sleep': median_sleep,
        # 'avg_insomnia': avg_insomnia,
        # 'median_insomnia': median_insomnia
    }



    #Create values and labels for barChart. 
    dates = hours_sleep_data(user_id, start_date, end_date)[0]
    data_points = hours_sleep_data(user_id, start_date, end_date)[1]

    bar_dict = {
        "labels" : dates,
        "datasets" : [
            {
                "fillColor" : "#48A497",
                "strokeColor" : "#48A4D1",
                "data" : data_points
            }]

    }


    #Create values and labels for lineChart. 
    data_points = sorted(db.session.query(Entry.date, Entry.insom_severity).filter\
        (Entry.user_id == user_id, Entry.date >= start_date, 
        Entry.date <= end_date).all())

    dates = []
    insom_severity_scores = []
    
    for item in data_points:
        date = "%s/%s" % (item[0].month, item[0].day)
        dates.append(date)

        insom_severity_score = item[1]
        insom_severity_scores.append(insom_severity_score)

    line_dict = {
        "labels": dates,
        "datasets": [
            {
                "label": "April",
                "fillColor": "rgba(220,220,220,0.2)",
                "strokeColor": "rgba(220,220,220,1)",
                "pointColor": "rgba(220,220,220,1)",
                "pointStrokeColor": "#fff",
                "pointHighlightFill": "#fff",
                "pointHighlightStroke": "rgba(220,220,220,1)",
                "data": insom_severity_scores
            },
            # {
            #     "label": "Cantaloupe",
            #     "fillColor": "rgba(151,187,205,0.2)",
            #     "strokeColor": "rgba(151,187,205,1)",
            #     "pointColor": "rgba(151,187,205,1)",
            #     "pointStrokeColor": "#fff",
            #     "pointHighlightFill": "#fff",
            #     "pointHighlightStroke": "rgba(151,187,205,1)",
            #     "data": [28, 48, 40, 19, 86, 27, 90]
            # }
        ]
    }


    #Calculate averages and medians from start_date to end_date.
    avg_sleep = "{0:.1f}".format(calculate_avg_sleep(user_id, start_date, end_date))
    median_sleep = "{0:.1f}".format(calculate_median_sleep(user_id, start_date, end_date))
    avg_insomnia = "{0:.1f}".format(calculate_avg_insom_severity(user_id, start_date, end_date))
    median_insomnia = "{0:.1f}".format(calculate_median_insom_severity\
                                        (user_id, start_date, end_date))
    avg_median_dict = {
        'avg_sleep': avg_sleep,
        'median_sleep': median_sleep,
        'avg_insomnia': avg_insomnia,
        'median_insomnia': median_insomnia
    }


    #Jsonify values and labels for each chart.
    data_list_of_dicts = {

        "bar_chart": bar_dict,
        "line_chart": line_dict,
        "donut_chart": donut_dict,
        "avg_median": avg_median_dict
    }
    
    
    return jsonify(data_list_of_dicts)
  



# @app.route('/insom-severity.json')
# def insom_severity_data():
#     """Returns a jsonified dictionary of values needed to create and update
#     the insom_severity line graph."""

    # user_id = 1
    # start_date = datetime(2016, 4, 1)
    # end_date = datetime(2016,4,30)

    #REFACTOR: move data formatting to helper.py! THEN TEST! 
    #Create a list of dates and a list of corresponding insom_severity_scores.
    


# @app.route("/hours-sleep.json")
# def hours_sleep_json():
#     """Returns a jsonified dictionary of values needed to create and update
#     the hours_sleep bar chart."""

#     user_id = 1

    #REFACTOR!!! MOVE TO HELPER FUNCTION.
    #If no dates selected, use date of user's first entry as default_start_date
    #and date of last_entry as user's default_end-date. If dates specified, 
    #use selected dates. 
    # default_start_date = datetime.strftime(two_weeks_before_last_entry(user_id), '%Y-%m-%d')
    # start = request.args.get("start_date", default_start_date)
    # start_date = datetime.strptime(start, '%Y-%m-%d')

    # start_date = datetime(2016, 5, 20) # HARDCODED, replace with function! 

    # default_end_date = datetime.strftime(last_entry(user_id), '%Y-%m-%d')
    # end = request.args.get("end_date", default_end_date)
    # end_date = datetime.strptime(end, '%Y-%m-%d')







###################################################################


if __name__ == "__main__":

    app.debug = True
    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run()

