"""Insomnia App"""

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from jinja2 import StrictUndefined

#NEED TO IMPORT MODELS
from model import connect_to_db, db, User, Entry

app = Flask(__name__)
#WHAT IS THIS?
app.secret_key = "ABC"
app.jinja_env.undefined = StrictUndefined

###################################################################


@app.route('/')
def index():
    """Display today's entry form."""

    return render_template("homepage.html")

@app.route('/dashboard')
def dashboard():
    """Display user's dashboard."""

    return render_template("dashboard.html")


###################################################################

if __name__ == "__main__":

    app.debug = True
    #connect_to_db(app)

    DebugToolbarExtension(app)

    app.run()


# 1. Make a form route & form html template.
# 1b. Can form fields be dependent on answer to previous form field?
# 2. Add data from form to database.
# 3. Test db

