"""Seed insomnia database with data from sample user."""

from sqlalchemy import func
from model import User, Entry
from datetime import date, time, datetime
from model import connect_to_db, db
from server import app



def load_entries():
    """Load entries from user_entries.csv into database."""

    User.query.delete()
    
    user = User(user_id=1,
                age=30,
                gender='female',
                zipcode='94110',
                first_name='Kelli',
                email='kwisuri@gmail.com',
                password='booger')

    db.session.add(user)
    db.session.commit()





    print "Entries"
    #Empty table before seeding data. 
    Entry.query.delete()

    for row in open("seed_data/user_entries_2.csv"):
        
        row = row.rstrip()
        user_id, date, minutes_asleep, insomnia, insom_type, insom_severity, alcohol, caffeine, menstruation, bedtime, stress_level, activity_level = row.split(",")
        date = datetime.strptime(date, '%m/%d/%Y')
        bedtime = datetime.strptime(bedtime, '%H:%M:%S')
        user_id = int(user_id)
        minutes_asleep = int(minutes_asleep)
        stress_level = int(stress_level)
        activity_level = int(activity_level)

        if insom_severity:
            insom_severity = int(insom_severity)
        else:
            insom_severity = 0

        #Instantiates entries.
        entry = Entry(user_id=user_id,
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

        #Adds entries to database.
        db.session.add(entry)

    db.session.commit()




if __name__ == "__main__":
    connect_to_db(app)

    #In case tables haven't been created, create them.
    db.create_all()

    #Import data.
    load_entries()



