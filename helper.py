from sqlalchemy import func, desc
from model import connect_to_db, db, User, Entry
import numpy as np
from datetime import datetime, date, timedelta

##################################################
# Database queries, data-formatting, and logic for server.py.
# IF TIME, REFACTOR TO FORMAT RESULTS OF FUNCTIONS HERE INSTEAD OF IN HTML 
# & SERVER FILE. 


def convert_to_boolean(value):
    if value == 'True':
        value = True
    else:
        value = False

    return value



def median(lst):
    """Calculates the median value in a list of numbers."""

    if len(lst) < 1:
            return None
    if len(lst) %2 == 1:
            return lst[((len(lst)+1)/2)-1]
    else:
            return float(sum(lst[(len(lst)/2)-1:(len(lst)/2)+1]))/2.0



def calculate_similarity(list1, list2):
    """Returns the percentage co-occurrence between two lists of values. Used to
    determine possible associations between behavioral factors and 
    insomnia."""

    a = np.array(list1)
    b = np.array(list2)
    similarity = np.mean(a == b)
    return similarity



def calculate_avg_sleep(user_id, start_date, end_date):
    """Calculates user's all-time average hours of sleep per night."""

    avg_sleep = db.session.query(func.avg(Entry.minutes_asleep)).filter(Entry.user_id\
     == user_id, Entry.date >= start_date, Entry.date <= end_date)
    avg_sleep = int(avg_sleep[0][0])/60.0
    return avg_sleep



def calculate_avg_insom_severity(user_id, start_date, end_date):
    """Calculates user's all-time average insomnia severity level."""

    avg_insom_severity = db.session.query(func.avg(Entry.insom_severity)).filter\
                        (Entry.user_id == user_id, Entry.date >= start_date, \
                            Entry.date <= end_date)
    avg_insom_severity = avg_insom_severity[0][0]
    return avg_insom_severity



def calculate_median_sleep(user_id, start_date, end_date):
    """Calculates user's all-time median hours of sleep per night."""

    minutes_asleep_tups = db.session.query(Entry.minutes_asleep).filter\
                            (Entry.user_id == user_id, Entry.date >= start_date,\
                            Entry.date <= end_date).order_by('minutes_asleep').all()
    
    minutes_asleep_lst = []
    for item in minutes_asleep_tups:
        minutes_asleep_lst.append(item[0])

    median_sleep = median(minutes_asleep_lst) / 60
    return median_sleep



def calculate_median_insom_severity(user_id, start_date, end_date):
    """Calculates user's all-time median insomnia severity level."""
    
    insom_severity_tups = db.session.query(Entry.insom_severity).filter\
                            (Entry.user_id == user_id, Entry.date >= start_date,\
                            Entry.date <= end_date).order_by('insom_severity').all()

    insom_severity_lst = []
    for item in insom_severity_tups:
        insom_severity_lst.append(item[0])

    median_insom_severity = median(insom_severity_lst)
    return median_insom_severity



def insom_type_frequency(user_id, start_date, end_date):
    """Returns a list of tuples. Each tuple includes insomnia_type, count of 
    insomnia_type occurrences between start date and end date, inclusive."""

    insom_type_frequency = db.session.query(Entry.insom_type, db.func.count\
                            (Entry.insom_type)).filter(Entry.user_id == user_id,\
                            Entry.date >= start_date, Entry.date <= end_date).\
                            group_by(Entry.insom_type).all()

    return insom_type_frequency

    

def most_frequent_type(user_id, start_date, end_date):
    """Returns a tuple that includes most frequently occurring insomnia_type,
    number of insomnia_type occurrences for user with user_id between 
    start_date and end_date, inclusive."""

    insom_type = sorted(insom_type_frequency(user_id, start_date, end_date))

    max_number = 0
    for item in insom_type:
        if item[0] != '':
            if int(item[1]) > max_number:
                max_number = item[1]
                name = item[0]
    return max_number, name



# def insom_and_alcohol(user_id):
#     """Returns the percentage co-occurrence between insomnia and alcohol
#     consumption."""

#     query_list = db.session.query(Entry.insomnia, Entry.alcohol).filter\
#     (Entry.user_id == user_id).order_by('date').all()

#     insom_list = []
#     alcohol_list = []

#     for item in query_list:
#         insom_list.append(item[0])
#         alcohol_list.append(item[1])

#     insom_and_alcohol = calculate_similarity(insom_list, alcohol_list)

#     return insom_and_alcohol



def hours_sleep_data(user_id, start_date, end_date):
    """Returns a list of 2 lists: the first is a list of dates as strings,
    the second is a list of hours_sleep data points as integers."""

    data_points = sorted(db.session.query(Entry.date, Entry.minutes_asleep).filter
        (Entry.user_id == user_id, Entry.date>= start_date, Entry.date <= 
        end_date).all())


    dates = []
    hours_sleep_list = []

    for item in data_points:
        date = "%s/%s" % (item[0].month, item[0].day)
        dates.append(date)

        hours_sleep = item[1]  / 60
        hours_sleep_list.append(hours_sleep)

    return dates, hours_sleep_list



def first_entry(user_id):
    """Returns date of user's first entry as a datetime object."""

    first_entry = db.session.query(Entry.date).filter(Entry.user_id == user_id).\
    order_by('date').first()

    return first_entry[0]



def last_entry(user_id):
    """Returns date of user's last entry as a datetime object."""

    last_entry = db.session.query(Entry.date).filter(Entry.user_id == user_id).\
    order_by(desc('date')).first()

    return last_entry[0]



def two_weeks_before_last_entry(user_id):
    """Returns date of entry two weeks before user's last entry as a datetime object."""

    two_weeks_date = last_entry(user_id) - timedelta(days=14)

    return two_weeks_date



def create_or_update_record(user_id, date, minutes_asleep, insomnia, insom_type,
                            insom_severity, alcohol, caffeine, menstruation,
                            bedtime, stress_level, activity_level):
    """If no existing record with user_id=user_id and date=date, 
    creates it. If existing record, updates the values."""

    if not db.session.query(Entry.user_id).filter(Entry.user_id == user_id, \
                                                Entry.date == date).first():
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

    else:
        entry_id = db.session.query(Entry.entry_id).filter(Entry.user_id == user_id,
                                                            Entry.date == date).first()
        entry = Entry.query.get(entry_id)

        entry.minutes_asleep = minutes_asleep,
        entry.insomnia = insomnia,
        entry.insom_type = insom_type,
        entry.insom_severity = insom_severity,
        entry.alcohol = alcohol,
        entry.caffeine = caffeine,
        entry.menstruation = menstruation,
        entry.bedtime = bedtime,
        entry.stress_level = stress_level,
        entry.activity_level = activity_level
        
        db.session.commit()







###################################################################

if __name__ == "__main__":

    app.debug = True
    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run()
