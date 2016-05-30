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

consumer_key = os.environ['client_id']
consumer_secret = os.environ['client_secret']
access_token = os.environ['access_token']
refresh_token = os.environ['refresh_token']


@app.route('/')
def index():
    """Display today's entry form."""

    authd_client = fitbit.Fitbit(consumer_key, consumer_secret,
                             access_token=access_token, refresh_token=refresh_token)
    sleep_log = authd_client.sleep()
    hours_sleep = sleep_log['summary']['totalMinutesAsleep'] / 60

    #Alert user!!!

    return render_template("homepage.html", 
                                hours_sleep = hours_sleep)



##########################################################################


@app.route('/dashboard', methods=["POST"])
def dashboard():
    """Display user's dashboard."""

    # Retrieve form data. 
    #ADD CHECK FOR DATES -- DOES USER HAVE ENTRIES FOR DATE RANGE ENTERED? 
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



    # Pass calculated data to template
    return render_template("dashboard2.html")


##########################################################################


@app.route('/insom-types.json')
def insom_type_data():
    """Returns a jsonified dictionary of values needed to create charts."""
 
    user_id = 1

    #Set dates
    default_start_date = datetime.strftime(four_weeks_before_last_entry(user_id), '%Y-%m-%d')
    start = request.args.get("start_date", default_start_date)
    if start == "":
        start = default_start_date
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = start_date + timedelta(28)


    #Create values & labels for donutChart. 
    a = frequency_insomnia_type(user_id, start_date, end_date, '')
    b = frequency_insomnia_type(user_id, start_date, end_date, 'early-awakening')
    c = frequency_insomnia_type(user_id, start_date, end_date, 'sleep-maintenance')
    d = frequency_insomnia_type(user_id, start_date, end_date, 'sleep-onset')

    type_dict = {
        "early-awakening": b,
        "sleep-maintenance": c,
        "sleep-onset": d
    }
    
    most_frequent_type = max(type_dict)

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
            }],

        'most_frequent_type': most_frequent_type
    }



    #Create values and labels for barChart. 
    dates = hours_sleep_data(user_id, start_date, end_date)[0]
    hours_sleep_scores = hours_sleep_data(user_id, start_date, end_date)[1]

    bar_dict = {
        "labels" : dates,
        "datasets" : [
            {
                "label" : "Hours Slept Per Night",
                "fillColor" : "#48A497",
                "strokeColor" : "#48A4D1",
                "data" : hours_sleep_scores
            }]
    }




    #Create values and labels for insomnia severity vs. stress lineChart. 
    insom_severity_scores = integer_type_data(user_id, start_date, end_date, 
                                                column_name=Entry.insom_severity)[1]

    stress_scores = integer_type_data(user_id, start_date, end_date,
                                        column_name=Entry.stress_level)[1]

    line_dict = {
        "labels": dates,
        "datasets": [
            {
                "label": "Insomnia Severity",
                "fillColor": "rgba(220,220,220,0.2)",
                "strokeColor": "rgba(220,220,220,1)",
                "pointColor": "rgba(220,220,220,1)",
                "pointStrokeColor": "#fff",
                "pointHighlightFill": "#fff",
                "pointHighlightStroke": "rgba(220,220,220,1)",
                "data": insom_severity_scores
            },
            {
                "label": "Stress Level",
                "fillColor": "rgba(151,187,205,0.2)",
                "strokeColor": "rgba(151,187,205,1)",
                "pointColor": "rgba(151,187,205,1)",
                "pointStrokeColor": "#fff",
                "pointHighlightFill": "#fff",
                "pointHighlightStroke": "rgba(151,187,205,1)",
                "data": stress_scores
            }
        ]
    }



    #Create values and lables for insomnia severity vs. activity level line chart. 
    activity_scores = integer_type_data(user_id, start_date, end_date,
                                        column_name=Entry.activity_level)[1]

    activity_line_dict = {
        "labels": dates,
        "datasets": [
            {
                "label": "Insomnia Severity",
                "fillColor": "rgba(220,220,220,0.2)",
                "strokeColor": "rgba(220,220,220,1)",
                "pointColor": "rgba(220,220,220,1)",
                "pointStrokeColor": "#fff",
                "pointHighlightFill": "#fff",
                "pointHighlightStroke": "rgba(220,220,220,1)",
                "data": insom_severity_scores
            },
            {
                "label": "Stress Level",
                "fillColor": "rgba(151,187,205,0.2)",
                "strokeColor": "rgba(151,187,205,1)",
                "pointColor": "rgba(151,187,205,1)",
                "pointStrokeColor": "#fff",
                "pointHighlightFill": "#fff",
                "pointHighlightStroke": "rgba(151,187,205,1)",
                "data": activity_scores
            }
        ]
    }



    #Create values and labels for avg_insom_severity_over_time line chart. 
    avg_insom = calculate_avg_insom_severity_over_time(user_id, 
                                                        first_entry(user_id), 
                                                        last_entry(user_id))

    avg_dates = avg_insom[1]
    avg_insom_severity_scores = avg_insom[0]

    avg_line_dict = {
    "labels": avg_dates,
    "datasets": [
        {
            "label": "Insomnia Severity",
            "fillColor": "rgba(220,220,220,0.2)",
            "strokeColor": "rgba(220,220,220,1)",
            "pointColor": "rgba(220,220,220,1)",
            "pointStrokeColor": "#fff",
            "pointHighlightFill": "#fff",
            "pointHighlightStroke": "rgba(220,220,220,1)",
            "data": avg_insom_severity_scores
        }
    ]
}



    #Calculate averages and medians from start_date to end_date.
    avg_sleep = "{0:.1f}".format(calculate_avg_sleep(user_id, start_date, end_date))
    median_sleep = "{0:.1f}".format(calculate_median_sleep(user_id, start_date, 
                                                    end_date))
    avg_insomnia = "{0:.1f}".format(calculate_avg(user_id, start_date, end_date,
                                                    column_name=Entry.insom_severity))
    median_insomnia = "{0:.1f}".format(calculate_median(user_id, 
                                                        start_date, 
                                                        end_date,
                                                        column_name="insom_severity"))
    avg_stress = "{0:.1f}".format(calculate_avg(user_id, start_date, end_date,
                                                column_name=Entry.stress_level))
    avg_activity = "{0:.1f}".format(calculate_avg(user_id, start_date, end_date,
                                                column_name=Entry.activity_level))
    median_stress = "{0:.1f}".format(calculate_median(user_id, 
                                                    start_date, 
                                                    end_date,
                                                    column_name="stress_level"))
    median_activity = "{0:.1f}".format(calculate_median(user_id, 
                                                        start_date, 
                                                        end_date,
                                                        column_name="activity_level"))

    print "AVG act", avg_activity
    print "AVG stress", avg_stress
    print "median_activity", median_activity
    print "median_stress", median_stress


    insom_factor = strongest_insom_factor(user_id, start_date, end_date)

    avg_median_dict = {
        'avg_sleep': avg_sleep,
        'median_sleep': median_sleep,
        'avg_insomnia': avg_insomnia,
        'median_insomnia': median_insomnia, 
        'insom_factor' : insom_factor,
        'avg_stress': avg_stress,
        'median_stress': median_stress,
        'avg_activity': avg_activity,
        'median_activity': median_activity
    }



    #Jsonify values and labels for each chart.
    data_list_of_dicts = {

        "bar_chart": bar_dict,
        "line_chart": line_dict,
        "activity_line_chart": activity_line_dict,
        "donut_chart": donut_dict,
        "avg_median": avg_median_dict,
        "avg_line_chart": avg_line_dict
    } 


    return jsonify(data_list_of_dicts)
  


###################################################################


if __name__ == "__main__":

    app.debug = True
    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run()

