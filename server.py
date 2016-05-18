"""Insomnia App"""

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import connect_to_db, db, User, Entry
from datetime import datetime, time, date
from sqlalchemy import func
from helper import *
import numpy as np

app = Flask(__name__)
app.secret_key = "DOESNTMATTER"
app.jinja_env.undefined = StrictUndefined

###################################################################


@app.route('/')
def index():
    """Display today's entry form."""

    return render_template("homepage.html")


##########################################################################


@app.route('/dashboard', methods=["POST"])
def dashboard():
    """Display user's dashboard."""

    # Passes form data to create new record in Entry table. 
    # user_id HARCODED NOW, GET ID FROM SESSION ONCE LOGIN COMPLETE
    user_id = 1 
    date = datetime.now()
    minutes_asleep = int((float(request.form.get("hours_sleep"))) * 60)

    insomnia = request.form.get("insomnia")
    if insomnia == 'True':
        insomnia = True
    else:
        insomnia = False

    insom_type = request.form.get("insom_type")
    insom_severity = int(request.form.get("insom_severity"))

    alcohol = request.form.get("alcohol")
    if alcohol == 'True':
        alcohol = True
    else:
        alcohol = False

    caffeine = request.form.get("caffeine")
    if caffeine == 'True':
        caffeine = True
    else:
        caffeine = False

    menstruation = request.form.get("menstruation")
    if menstruation == 'True':
        menstruation = True
    else:
        menstruation = False
    
    bedtime = request.form.get("bedtime")
    bedtime = datetime.strptime(bedtime, '%H:%M')
    stress_level = int(request.form.get("stress_level"))
    activity_level = int(request.form.get("activity_level"))

    new_entry = Entry(user_id=user_id,
                        date=date,
                        minutes_asleep=minutes_asleep,
                        insomnia=insomnia,
                        insom_type=insom_type,
                        insom_severity=insom_severity,
                        alcohol=alcohol,
                        caffeine=caffeine,
                        menstruation=menstruation,
                        bedtime=bedtime,
                        stress_level=stress_level,
                        activity_level=activity_level)

    db.session.add(new_entry)
    db.session.commit()

##########################################################################
    # Data insights
    
    #HARDCODED FOR NOW.
    start_date = datetime(2016, 4, 1)
    end_date = datetime(2016,5,1)

    # Calculate average sleep per night
    avg_sleep = calculate_avg_sleep(user_id)

    # Calculate average insomnia severity
    avg_insom_severity = calculate_avg_insom_severity(user_id)

    # Calculate median sleep per night
    median_sleep = calculate_median_sleep(user_id)

    # Calculate median insomnia severity
    median_insom_severity = calculate_median_insom_severity(user_id)

    #Calculate co-occurrence between insomnia and alcohol consumption
    insom_and_alcohol_co_occurrence = insom_and_alcohol(user_id)

    #Calculate all-time most frequently occurring type of insomnia
    most_frequent_type_insomnia = most_frequent_type(user_id, start_date, end_date)
    most_frequent_type_insomnia = most_frequent_type_insomnia[1]

##########################################################################
    # Pass calculated data to template
    
    return render_template("dashboard2.html", 
                                avg_sleep=avg_sleep,
                                median_sleep=median_sleep,
                                avg_insom_severity=avg_insom_severity,
                                median_insom_severity=median_insom_severity,
                                insom_and_alcohol_co_occurrence=insom_and_alcohol_co_occurrence,
                                most_frequent_type_insomnia=most_frequent_type_insomnia)


##########################################################################


@app.route('/user-data.json')
def retrieve_insom_severity():
    """Returns a list of insom_severity data points & corresponding date for 
    user with user_id, from start_date to end_date, inclusive."""
 
    user_id = 1
    start_date = datetime(2016, 4, 1)
    end_date = datetime(2016,5,1)

    data_points = db.session.query(Entry.insom_severity, Entry.date).filter\
        (Entry.user_id == user_id, Entry.date >= start_date, 
        Entry.date <= end_date).all()

    d = {}
    for item in data_points:
        date = "%s/%s" % (item[1].month, item[1].day)
        d[date] = item[0]

    return jsonify(d)


##########################################################################

#Queries db for insomnia type data; inserts data into dictionary used to
#create insomnia type donut chart.
@app.route('/insom-types.json')
def melon_types_data():
    """Return data about Melon Sales."""

    # VARIABLES HARDCODED NOW, BUT I CAN CHANGE ONCE I SETTLE ON USER EXPERIENCE. 
    user_id = 1
    start = request.args.get("start_date", "2016-02-01")#query db for first entry
    print "START", start
    end = request.args.get("end_date", "2016-03-01")
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')
    print start_date
    print end_date

    # start_date = datetime(2016, 4, 1)
    # end_date = datetime(2016, 4, 30)
    
    #Calculate total days in time range
    total_days = end_date - start_date
    total_days = total_days.days + 1

    #Calculate frequency of each insomnia type
    insom_type = insom_type_frequency(user_id, start_date, end_date)
    insom_type = sorted(insom_type)
    x_percentage = float(insom_type[0][1]) / total_days * 100

    x = '{0:.0f}'.format(float(insom_type[0][1]) / total_days * 100)
    x_label = "No insomnia"
    y = '{0:.0f}'.format(float(insom_type[1][1]) / total_days * 100)
    y_label = "Early-awakening insomnia"
    z = '{0:.0f}'.format(float(insom_type[2][1]) / total_days * 100)
    z_label = "Sleep-maintenance insomnia"
    a = '{0:.0f}'.format(float(insom_type[3][1]) / total_days * 100)
    a_label = "Sleep-onset insomnia"


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
        ]
    }
    return jsonify(data_list_of_dicts)
  

#Queries db for insomnia severity data; inserts data into dictionary used to
#create insomnia severity line graph. 
@app.route('/insom-severity.json')
def melon_times_data():
    """Return time series data of Melon Sales."""

    user_id = 1
    start_date = datetime(2016, 4, 1)
    end_date = datetime(2016,4,30)

    data_points = sorted(db.session.query(Entry.date, Entry.insom_severity).filter\
        (Entry.user_id == user_id, Entry.date >= start_date, 
        Entry.date <= end_date).all())


    dates = []
    insom_severity_scores = []
    
    for item in data_points:
        # date = item[0].weekday()
        # if date == 0:
        #     date = 'Mon'
        # elif date == 1:
        #     date = 'Tue'
        # elif date == 2:
        #     date = 'Wed'
        # elif date == 3:
        #     date = 'Thu'
        # elif date == 4:
        #     date = 'Fri'
        # elif date == 5:
        #     date = 'Sat'
        # else:
        #     date = 'Sun'

        date = "%s/%s" % (item[0].month, item[0].day)
        dates.append(date)

        insom_severity_score = item[1]
        insom_severity_scores.append(insom_severity_score)



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

