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


# Import Fitbit credentials. 
# NOTE: Fitbit integration just added. Currently no Fitbit table in data model, 
# so no way to check whether user has Fitbit or not. Add during Phase 3 refactor. 
consumer_key = os.environ['client_id']
consumer_secret = os.environ['client_secret']
access_token = os.environ['access_token']
refresh_token = os.environ['refresh_token']


@app.route('/')
def index():
    """Display homepage."""

    return render_template("index.html")


###################################################################


@app.route('/login')
def login():
    """Display login page."""

    return render_template("login.html")


###################################################################


@app.route('/verify-login', methods=["POST"])
def verify_login():

    username = request.form.get("username")
    password = request.form.get("password")

    user_object = User.query.filter_by(email=username).first()

    # If username exists in database:
    if user_object: 

        # If given password matches password in database:
        if password == user_object.password:

            # Add user to the session.
            session["user_id"] = user_object.user_id

            # Redirect to dashboard.
            return redirect('/entry')

        # If password doesn't match:
        else:
            flash("Your password is incorrect. Please try again.")
            return redirect('/login')

    # If user doesn't exist:
    else:
        flash("You're not registered. Please register here.")
        return redirect('/register')
 

###################################################################


@app.route('/register')
def register():
    """Displays user registration page."""

    return render_template("register.html")


###################################################################


@app.route('/verify-registration', methods=["POST"])
def verify_registration():
    """Creates new user. If user already exists, redirects to login page."""

    username = request.form.get("username")
    password = request.form.get("password")
    first_name = request.form.get("firstname")
    age = request.form.get("age")
    gender = request.form.get("gender")
    zipcode = request.form.get("zipcode")


    user = User.query.filter_by(email=username).first()

    # if user doesn't exist, create new user in db.
    if user == None:
        new_user = User(email=username, 
                        password=password, 
                        first_name=first_name, 
                        age=age,
                        gender=gender,
                        zipcode=zipcode)
        db.session.add(new_user)
        db.session.commit()

        flash("Thanks for registering! Please login.")

    # if user exists and password matches, redirect to login. If username
    # already taken, reload registration page. 
    elif user:
        if user.password == password:
            flash("You're already registered. Please login.")
        else:
            flash("That username is taken. Please choose another username.")
            return redirect('/register')

    return redirect('/login')



###################################################################


@app.route('/logout')
def logout():

    del session['user_id']
    flash("You've been logged out.")

    return redirect('/')


###################################################################


@app.route('/entry')
def form():
    """Display today's entry form."""

    #NOTE: Calling Fitbit API using Python Fitbit library, which only provides
    #limited user data. For more data, must make a manual request to Fitbit API.

    #NOTE: Accessing user data via implicit grant authorization flow. This auth 
    #flow only works for the currently logged in user. For increased security 
    #and app usage by others, must implement OAuth. 

    authd_client = fitbit.Fitbit(consumer_key, consumer_secret,
                             access_token=access_token, refresh_token=refresh_token)
    sleep_log = authd_client.sleep()
    hours_sleep = sleep_log['summary']['totalMinutesAsleep'] / 60

    return render_template("entry.html", 
                                hours_sleep = hours_sleep)


##########################################################################


@app.route('/dashboard', methods=["POST"])
def dashboard():
    """Display user's dashboard."""

    # Retrieve form data. 
    user_id = session["user_id"]
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
    return render_template("dashboard.html")


##########################################################################


@app.route('/insom-types.json')
def insom_type_data():
    """Returns a jsonified dictionary of values needed to create charts."""
 
    user_id = session["user_id"]

    # Set dates.
    # NOTE: Implement check for date ranges during Phase 3 refactor. Does user 
    # have entries for date_range entered by user? If not, what happens?
    default_start_date = datetime.strftime(four_weeks_before_last_entry(user_id), '%Y-%m-%d')
    start = request.args.get("start_date", default_start_date)
    if start == "":
        start = default_start_date 
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = start_date + timedelta(28)


    # Create values & labels for donutChart.
    insom_type_dict = frequency_insomnia_type_formatted(user_id, 
                                                        start_date, end_date)
    most_frequent_type = most_frequent_insom_type(user_id, start_date, end_date)

    donut_dict = {
        'insom_type': [
            {
                "value": insom_type_dict["none"], 
                "color": "#A9A9A9",
                "highlight": "#808080",
                "label": "No insomnia yay!"
            },
            {
                "value": insom_type_dict["early-awakening"],
                "color": "#46BFBD",
                "highlight": "#5AD3D1",
                "label": "Early-awakening insomnia"
            },
            {
                "value": insom_type_dict["sleep-maintenance"],
                "color": "#F7464A",
                "highlight": "#FF5A5E",
                "label": "Sleep-maintenace insomnia"
            },
            {
                "value": insom_type_dict["sleep-onset"],
                "color": "#FDB45C",
                "highlight": "#FFC870",
                "label": "Sleep-onset insomnia"
            }],

        'most_frequent_type': most_frequent_type
    }



    #Create values and labels for hours_sleep barChart. 
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
                "label": "Activity Level",
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



    # Calculate textual insights from start_date to end_date.
    avg_sleep = "{0:.1f}".format(calculate_avg_sleep(user_id, start_date, end_date))
    median_sleep = "{0:.1f}".format(calculate_median_sleep(user_id, start_date, 
                                                    end_date))
    avg_insomnia = "{0:.1f}".format(calculate_avg(user_id, start_date, end_date,
                                                    column_name=Entry.insom_severity))
    median_insomnia = "{0:.1f}".format(calculate_median(user_id, 
                                                        start_date, 
                                                        end_date,
                                                        column_name=Entry.insom_severity))
    avg_stress = "{0:.1f}".format(calculate_avg(user_id, start_date, end_date,
                                                column_name=Entry.stress_level))
    avg_activity = "{0:.1f}".format(calculate_avg(user_id, start_date, end_date,
                                                column_name=Entry.activity_level))
    median_stress = "{0:.1f}".format(calculate_median(user_id, 
                                                    start_date, 
                                                    end_date,
                                                    column_name=Entry.stress_level))
    median_activity = "{0:.1f}".format(calculate_median(user_id, 
                                                        start_date, 
                                                        end_date,
                                                        column_name=Entry.activity_level))
    insom_factor = strongest_insom_factor(user_id, 
                                            first_entry(user_id),
                                            last_entry(user_id))
    insom_factor_insight_text = insom_factor_text(user_id, start_date, end_date)
    all_time_insom_type_dict = frequency_insomnia_type_formatted(user_id, 
                                                        first_entry(user_id), 
                                                        last_entry(user_id))
    all_time_most_frequent_type = most_frequent_insom_type(user_id, 
                                                        first_entry(user_id), 
                                                        last_entry(user_id))
    most_frequent_insom_type_text = most_frequent_type_text(all_time_most_frequent_type)

    avg_median_dict = {
        'avg_sleep': avg_sleep,
        'median_sleep': median_sleep,
        'avg_insomnia': avg_insomnia,
        'median_insomnia': median_insomnia,
        'insom_factor': insom_factor,
        'insom_factor_insight_text': insom_factor_insight_text,
        'avg_stress': avg_stress,
        'median_stress': median_stress,
        'avg_activity': avg_activity,
        'median_activity': median_activity,
        'all_time_most_frequent_type': all_time_most_frequent_type,
        'most_frequent_insom_type_text': most_frequent_insom_type_text
    }


    #Jsonify values and labels for each chart.
    data_list_of_dicts = {

        "bar_chart": bar_dict,
        "line_chart": line_dict,
        "activity_line_chart": activity_line_dict,
        "donut_chart": donut_dict,
        "avg_median": avg_median_dict
    } 


    return jsonify(data_list_of_dicts)
  

###################################################################


if __name__ == "__main__":

    app.debug = True
    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run()

