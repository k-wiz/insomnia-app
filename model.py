
"""Models and database functions for Insomnia App."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

######################################################
# Model definitions 

class User(db.Model):
    """User of Insomnia App."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(15), nullable=False)
    zipcode = db.Column(db.String(15), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)

    entries = db.relationship('Entry')


    def __repr__(self):
        """Helpful representation of user object instance when printed."""

        return "<User user_id={} first_name={}>".format(self.user_id, 
                                                        self.first_name)


class Entry(db.Model):
    """Daily entry by user of insomnia & sleep-related data.""" 

    __tablename__ = "entries"

    entry_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hours_sleep = db.Column(db.Float, nullable=False)
    insomnia = db.Column(db.Boolean, nullable=False)
    insom_type = db.Column(db.String(65), nullable=True) # Nullable, will filter out NULLs
    insom_severity = db.Column(db.Integer, nullable=False, default=0) # Non-nullable, default value 0
    alcohol = db.Column(db.Boolean, nullable=False)
    caffeine = db.Column(db.Boolean, nullable=False)
    menstruation = db.Column(db.Boolean, nullable=False)
    bedtime = db.Column(db.Time, nullable=False)
    stress_level = db.Column(db.Integer, nullable=False) 
    activity_level = db.Column(db.Integer, nullable=False)

    user = db.relationship('User')


    def __repr__(self):
        """Helpful representation of entry object instance when printed."""

        return "<User user_id={} date={}>".format(self.user_id, self.date)



#######################################################
# Helper functions


def connect_to_db(app):
    """Connect the database to Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///insomnia'
    db.app = app
    db.init_app(app)

if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."







# 1. Create data model: User, Entry classes
# 2. foreign key on Entry. (User.entries, Entry.User)
# 3. test queries -- can I get the data I want with my data structure?
# 4. Research & test data analysis. Can I get the insights I want?