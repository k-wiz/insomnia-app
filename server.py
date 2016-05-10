"""Insomnia App"""

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from jinja2 import StrictUndefined

#NEED TO IMPORT MODELS
from model import connect_to_db, db, User, Entry

app = Flask(__name__)
#WHAT IS THIS?
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

    #entry_id auto assigned
    user_id = 1 #get id from session
    #date = datetime.datetime.now()
    hours_sleep = request.form.get("hours_sleep")
    print "HOURS SLEEP", hours_sleep
    insomnia = request.form.get("insomnia")
    print "Insomnia", insomnia
    insom_type = request.form.get("insom_type")
    print "TYPE", insom_type
    insom_severity = request.form.get("insom_severity")
    print "SEVERITY", insom_severity
    alcohol = request.form.get("alcohol")
    print "alcohol", alcohol, type(alcohol)
    caffeine = request.form.get("caffeine")
    print "caffeine", caffeine
    menstruation = request.form.get("menstruation")
    print "menstruation", menstruation
    bedtime = request.form.get("bedtime")
    print "bedtime", bedtime, type(bedtime)
    stress_level = request.form.get("stress_level")
    print "stress", stress_level
    activity_level = request.form.get("activity_level")
    print "activity", activity_level

    # new_entry = Entry(user_id=user_id,
    #                     date=date,
    #                     hours_sleep=hours_sleep,
    #                     insomnia=insomnia,
    #                     insom_type=insom_type,
    #                     insom_severity=insom_severity,
    #                     alcohol=alcohol,
    #                     caffeine=caffeine,
    #                     menstruation=menstruation,
    #                     bedtime=bedtime,
    #                     stress_level=stress_level,
    #                     activity_level=activity_level)

    # db.session.add(new_entry)
    # db.session.commit()


    return render_template("dashboard.html")


###################################################################

if __name__ == "__main__":

    app.debug = True
    #connect_to_db(app)

    DebugToolbarExtension(app)

    app.run()

