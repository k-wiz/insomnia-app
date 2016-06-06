
"""Models and database functions for Insomnia App."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
    minutes_asleep = db.Column(db.Integer, nullable=False)
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


def connect_to_db(app, db_name='postgresql:///insomnia'):
    """Connect the database to Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = db_name
    db.app = app
    db.init_app(app)

def example_data():
    """Sample data for test database."""

    user1 = User(user_id=1, age=30, zipcode='94110', gender='F', first_name='Kelli', password='peanut', 
                email='kelli@gmail.com')

    e1 = Entry(user_id=1, 
                date=datetime(2016,5,1), 
                minutes_asleep=420, 
                insomnia=True,
                insom_type='early-awakening',
                insom_severity=1,
                alcohol=False,
                caffeine=True,
                menstruation=False,
                bedtime='23:00',
                stress_level=3,
                activity_level=4)

    e2 = Entry(user_id=1, 
                date=datetime(2016,5,2), 
                minutes_asleep=420, 
                insomnia=True,
                insom_type='sleep-maintenance',
                insom_severity=1,
                alcohol=False,
                caffeine=True,
                menstruation=False,
                bedtime='23:00',
                stress_level=3,
                activity_level=4)

    e3 = Entry(user_id=1, 
                date=datetime(2016,5,3), 
                minutes_asleep=420, 
                insomnia=True,
                insom_type='sleep-onset',
                insom_severity=1,
                alcohol=False,
                caffeine=True,
                menstruation=False,
                bedtime='23:00',
                stress_level=3,
                activity_level=4)

    e4 = Entry(user_id=1, 
                date=datetime(2016,5,4), 
                minutes_asleep=420, 
                insomnia=True,
                insom_type='',
                insom_severity=1,
                alcohol=False,
                caffeine=True,
                menstruation=False,
                bedtime='23:00',
                stress_level=3,
                activity_level=4)

    e5 = Entry(user_id=1, 
                date=datetime(2016,5,5), 
                minutes_asleep=420, 
                insomnia=True,
                insom_type='',
                insom_severity=1,
                alcohol=False,
                caffeine=True,
                menstruation=False,
                bedtime='23:00',
                stress_level=3,
                activity_level=4)

    e6 = Entry(user_id=1, 
                date=datetime(2016,5,6), 
                minutes_asleep=420, 
                insomnia=True,
                insom_type='',
                insom_severity=1,
                alcohol=False,
                caffeine=True,
                menstruation=False,
                bedtime='23:00',
                stress_level=3,
                activity_level=4)

    e7 = Entry(user_id=1, 
                date=datetime(2016,5,7), 
                minutes_asleep=420, 
                insomnia=True,
                insom_type='',
                insom_severity=1,
                alcohol=False,
                caffeine=True,
                menstruation=False,
                bedtime='23:00',
                stress_level=3,
                activity_level=4)

    e8 = Entry(user_id=1, 
                date=datetime(2016,5,8), 
                minutes_asleep=420, 
                insomnia=True,
                insom_type='',
                insom_severity=1,
                alcohol=False,
                caffeine=True,
                menstruation=False,
                bedtime='23:00',
                stress_level=3,
                activity_level=4)

    db.session.add_all([user1, e1, e2, e3, e4, e5, e6, e7, e8])
    db.session.commit()


#########################################################

if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."


