"""Insomnia App"""

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import connect_to_db, db, User, Entry
from datetime import datetime, time, date
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

# consumer_key = os.environ['client_id']
# consumer_secret = os.environ['client_secret']
# access_token = os.environ['access_token']
# refresh_token = os.environ['refresh_token']
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

    #payload 
    r = requests.get("https://api.fitbit.com/1/user/-/sleep/date/2016-04-20.json")
    print "RRRRRRRR", r


    #If fitbit: 
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
    most_frequent_type_insomnia = (most_frequent_type(user_id, start_date, end_date))[1]


    # Pass calculated data to template
    return render_template("dashboard2.html", 
                                avg_sleep=avg_sleep,
                                median_sleep=median_sleep,
                                avg_insom_severity=avg_insom_severity,
                                median_insom_severity=median_insom_severity,
                                most_frequent_type_insomnia=most_frequent_type_insomnia)


##########################################################################


@app.route('/insom-types.json')
def insom_type_data():
    """Returns a jsonified dictionary of values needed to update the pie chart, 
    averages, and medians. First value is data needed to load chart.
    Last 4 values are data needed to display averages & medians."""
 
    user_id = 1

    # Default dashboard view shows all-time data, from user's first entry 
    # (default start date) to user's last entry (default_end_date). 
    default_start_date = datetime.strftime(first_entry(user_id), '%Y-%m-%d')
    start = request.args.get("start_date", default_start_date)
    start_date = datetime.strptime(start, '%Y-%m-%d')
    default_end_date = datetime.strftime(last_entry(user_id), '%Y-%m-%d')
    end = request.args.get("end_date", default_end_date)
    end_date = datetime.strptime(end, '%Y-%m-%d')
    
    #Calculate total days in time range
    total_days = end_date - start_date
    total_days = total_days.days + 1

    #NOTE: NEED TO ADD CONDITIONAL TO CHECK IF LIST IS LESS THAN
    #LENGTH OF 4. 
    #Calculate frequency of each insomnia type as a percentage
    insom_type = insom_type_frequency(user_id, start_date, end_date)
    insom_type = sorted(insom_type)

    x = '{0:.0f}'.format(float(insom_type[0][1]) / total_days * 100)
    x_label = "No insomnia"
    y = '{0:.0f}'.format(float(insom_type[1][1]) / total_days * 100)
    y_label = "Early-awakening insomnia"
    z = '{0:.0f}'.format(float(insom_type[2][1]) / total_days * 100)
    z_label = "Sleep-maintenance insomnia"
    a = '{0:.0f}'.format(float(insom_type[3][1]) / total_days * 100)
    a_label = "Sleep-onset insomnia"


    #Calculate averages and medians from start_date to end_date.
    avg_sleep = "{0:.1f}".format(calculate_avg_sleep(user_id, start_date, end_date))
    median_sleep = "{0:.1f}".format(calculate_median_sleep(user_id, start_date, end_date))
    avg_insomnia = "{0:.1f}".format(calculate_avg_insom_severity(user_id, start_date, end_date))
    median_insomnia = "{0:.1f}".format(calculate_median_insom_severity\
                                        (user_id, start_date, end_date))

    #UPDATE COLORS & LABELS
    data_list_of_dicts = {
        'insom_type': [
            {
                "value": x, 
                "color": "#A9A9A9",
                "highlight": "#808080",
                "label": x_label
            },
            {
                "value": y,
                "color": "#46BFBD",
                "highlight": "#5AD3D1",
                "label": y_label
            },
            {
                "value": z,
                "color": "#F7464A",
                "highlight": "#FF5A5E",
                "label": z_label
            },
            {
                "value": a,
                "color": "#FDB45C",
                "highlight": "#FFC870",
                "label": a_label
            }
        ],
        'avg_sleep': avg_sleep,
        'median_sleep': median_sleep,
        'avg_insomnia': avg_insomnia,
        'median_insomnia': median_insomnia
    }
    return jsonify(data_list_of_dicts)
  

############################################################################


@app.route('/insom-severity.json')
def insom_severity_data():
    """Returns a jsonified dictionary of values needed to create and update
    the insom_severity line graph."""

    user_id = 1
    start_date = datetime(2016, 4, 1)
    end_date = datetime(2016,4,30)

    #REFACTOR: move data formatting to helper.py! THEN TEST! 
    #Create a list of dates and a list of corresponding insom_severity_scores.
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


    #Pass lists of dates & insom_severity_scores to dictionary.

    data_dict = {
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
    return jsonify(data_dict)


###################################################################


if __name__ == "__main__":

    app.debug = True
    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run()

