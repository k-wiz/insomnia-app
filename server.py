"""Insomnia App"""

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import connect_to_db, db, User, Entry
from datetime import datetime, time, date
from sqlalchemy import func
from helper import median, calculate_avg_sleep, calculate_avg_insom_severity, \
                    calculate_median_sleep, calculate_median_insom_severity

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
    return render_template("dashboard.html", 
                                avg_sleep=avg_sleep,
                                median_sleep=median_sleep,
                                avg_insom_severity=avg_insom_severity,
                                median_insom_severity=median_insom_severity)


###################################################################

if __name__ == "__main__":

    app.debug = True
    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run()

