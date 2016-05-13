from sqlalchemy import func
from model import connect_to_db, db, User, Entry

##################################################

def median(lst):
    """Calculates the median value in a list of numbers."""

    if len(lst) < 1:
            return None
    if len(lst) %2 == 1:
            return lst[((len(lst)+1)/2)-1]
    else:
            return float(sum(lst[(len(lst)/2)-1:(len(lst)/2)+1]))/2.0


def calculate_avg_sleep(user_id):
    """Calculates user's all-time average hours of sleep per night."""

    avg_sleep = db.session.query(func.avg(Entry.minutes_asleep)).filter(Entry.user_id == user_id)
    avg_sleep = int(avg_sleep[0][0])/60.0
    return avg_sleep


def calculate_avg_insom_severity(user_id):
    """Calculates user's all-time average insomnia severity level."""

    avg_insom_severity = db.session.query(func.avg(Entry.insom_severity)).filter(Entry.user_id == user_id)
    avg_insom_severity = avg_insom_severity[0][0]
    return avg_insom_severity


def calculate_median_sleep(user_id):
    """Calculates user's all-time median hours of sleep per night."""

    minutes_asleep_tups = db.session.query(Entry.minutes_asleep).filter(Entry.user_id == user_id).order_by('minutes_asleep').all()
    
    minutes_asleep_lst = []
    for item in minutes_asleep_tups:
        minutes_asleep_lst.append(item[0])

    median_sleep = median(minutes_asleep_lst) / 60
    return median_sleep


def calculate_median_insom_severity(user_id):
    """Calculates user's all-time median insomnia severity level."""
    
    insom_severity_tups = db.session.query(Entry.insom_severity).filter(Entry.user_id == user_id).order_by('insom_severity').all()

    insom_severity_lst = []
    for item in insom_severity_tups:
        insom_severity_lst.append(item[0])

    median_insom_severity = median(insom_severity_lst)
    return median_insom_severity



def insom_type_frequency(user_id):
    """Returns count of insomnia_type occurrences."""

    insom_type_frequency = db.session.query(db.func.count(Entry.insom_type), \
                            Entry.insom_type).filter(Entry.user_id == user_id).\
                            group_by(Entry.insom_type).all()

    return insom_type_frequency














###################################################################

if __name__ == "__main__":

    app.debug = True
    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run()
