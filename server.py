"""Insomnia App"""

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import connect_to_db, db, User, Entry
from datetime import datetime, time, date
from sqlalchemy import func
from helper import median, calculate_avg_sleep, calculate_avg_insom_severity,\
 calculate_median_sleep, calculate_median_insom_severity, insom_type_frequency

app = Flask(__name__)
app.secret_key = "DOESNTMATTER"
app.jinja_env.undefined = StrictUndefined

###################################################################


@app.route('/')
def index():
    """Display today's entry form."""

    return render_template("homepage.html")


@app.route('/dashboard', methods=["POST"])
def dashboard():
    """Display user's dashboard."""


    # Uses form data to create new records in Entry table. 

    user_id = 1 #user_id hardcoded now; get id from session once login setup
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


    # Calculate average sleep per night
    avg_sleep = calculate_avg_sleep(user_id)

    # Calculate average insomnia severity
    avg_insom_severity = calculate_avg_insom_severity(user_id)

    # Calculate median sleep per night
    median_sleep = calculate_median_sleep(user_id)

    # Calculate median insomnia severity
    median_insom_severity = calculate_median_insom_severity(user_id)


    # Pass data to template
    return render_template("dashboard2.html", 
                                avg_sleep=avg_sleep,
                                median_sleep=median_sleep,
                                avg_insom_severity=avg_insom_severity,
                                median_insom_severity=median_insom_severity)


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


# @app.route('/insom-type-data.json')
# def retrieve_insom_type():
#     """Returns """

#     user_id = 1
#     start_date = datetime(2016, 4, 1)
#     end_date = datetime(2016, 5, 1)

#     insom_type = insom_type_frequency(user_id, start_date, end_date)

#     data_list_of_dicts = {
#         'melons': [
#             {
#                 "value": 300,
#                 "color": "#F7464A",
#                 "highlight": "#FF5A5E",
#                 "label": "Christmas Melon"
#             },
#             {
#                 "value": 50,
#                 "color": "#46BFBD",
#                 "highlight": "#5AD3D1",
#                 "label": "Crenshaw"
#             },
#             {
#                 "value": 100,
#                 "color": "#FDB45C",
#                 "highlight": "#FFC870",
#                 "label": "Yellow Watermelon"
#             }
#         ]
#     }
#     return jsonify(data_list_of_dicts)

@app.route('/insom-types.json')
def melon_types_data():
    """Return data about Melon Sales."""

    # These variables are hardcoded now, but can change once I add a login 
    # and a button that allows users to select dates. 

    user_id = 1
    start_date = datetime(2016, 4, 1)
    end_date = datetime(2016, 5, 1)

    insom_type = insom_type_frequency(user_id, start_date, end_date)


    x = insom_type[0][0]
    x_label = insom_type[0][1]
    y = insom_type[1][0]
    y_label = insom_type[1][1]
    z = insom_type[2][0]
    z_label = insom_type[2][1]
    a = insom_type[3][0]
    a_label = insom_type[3][1]

    data_list_of_dicts = {
        'insom_type': [
            {
                "value": x,
                "color": "#F7464A",
                "highlight": "#FF5A5E",
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
                "color": "#D3D3D3",
                "highlight": "#A9A9A9",
                "label": "none"
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
  







###################################################################

if __name__ == "__main__":

    app.debug = True
    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run()

