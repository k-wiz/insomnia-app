from sqlalchemy import func, desc
from model import connect_to_db, db, User, Entry
import numpy as np
from datetime import datetime, date, timedelta, time

##################################################
# Database queries, data-formatting, and logic for server.py.

def convert_to_boolean(value):
    if value == 'True':
        value = True
    else:
        value = False

    return value



# NOTE: Remove during Refactor Phase 2 and replace with built-in NumPy function. 
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



def key_of_largest_value(dict):
    """Returns key of largest value in dictionary if and only if the largest
    value > .5."""

    v = list(dict.values())
    k = list(dict.keys())
    return k[v.index(max(v))]



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



# NOTE: Generalize and rename function.
def four_weeks_before_last_entry(user_id):
    """Returns date of entry four weeks before user's last entry as a datetime object."""

    date = last_entry(user_id) - timedelta(days=28)

    return date



# NOTE: Collapse into calculate_avg during Phase 3 refactor. 
def calculate_avg_sleep(user_id, start_date, end_date):
    """Calculates user's average hours of sleep per night from start_date
    to end_date."""

    avg_sleep = db.session.query(func.avg(Entry.minutes_asleep)).filter(Entry.user_id\
     == user_id, Entry.date >= start_date, Entry.date <= end_date)
    avg_sleep = int(avg_sleep[0][0])/60.0
    return avg_sleep



def calculate_avg(user_id, start_date, end_date, column_name):
    """Calculates average of field with column_name from start_date to end_date."""

    avg = db.session.query(func.avg(column_name)).filter\
                        (Entry.user_id == user_id, Entry.date >= start_date, \
                            Entry.date <= end_date)
    avg = avg[0][0]
    return avg



def calculate_avg_sleep_over_time(user_id, start_date, end_date):
    """Calculates the average of each time interval from start_date to end_date.
    Returns a list of averages as floats and a list of dates as strings."""

    averages = []
    start_dates = []

    while start_date <= (end_date - timedelta(days=7)):
        interval_end_date = start_date + timedelta(days=7)
        avg = calculate_avg_sleep(user_id, start_date, interval_end_date)
        averages.append(avg)

        start_date = start_date + timedelta(days=7)
        date = "%s/%s" % (start_date.month, start_date.day)
        start_dates.append(date)

    return averages, start_dates



# def calculate_avg_insom_severity_over_time(user_id, start_date, end_date):
#     """Calculates the average of each time interval from start_date to end_date.
#     Returns a list of averages as floats and a list of dates as strings."""

#     averages = []
#     start_dates = []

#     while start_date <= (end_date - timedelta(days=7)):
#         interval_end_date = start_date + timedelta(days=7)
#         avg = float(calculate_avg(user_id, start_date, interval_end_date, 
#                                 column_name=Entry.insom_severity))
#         averages.append(avg)

#         start_date = start_date + timedelta(days=7)
#         date = "%s/%s" % (start_date.month, start_date.day)
#         start_dates.append(date)

#     return averages, start_dates



# NOTE: Collapse into calculate_median during Phase 3 refactor.
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



def calculate_median(user_id, start_date, end_date, column_name):
    """Calculates median value in a list of values returned from db query.
    column_name should be an object with attribute column_name, e.g. Entry.stress_level."""
    
    data_point_tuples = db.session.query(column_name).filter\
                            (Entry.user_id == user_id, Entry.date >= start_date,\
                            Entry.date <= end_date).all()

    data_points = []
    for item in data_point_tuples:
        data_points.append(item[0])

    median_value = median(sorted(data_points))

    return median_value



# NOTE: Refactor to return a dictionary of insom_type frequencies, with 
# insom_type as key and frequency as value.
def frequency_insomnia_type(user_id, start_date, end_date, insom_type):
    """Returns count of occurrence of insom_type from start_date to end_date."""

    frequency_type = db.session.query(Entry.insom_type, db.func.count\
                            (Entry.insom_type)).filter(Entry.user_id == user_id,\
                            Entry.date >= start_date, Entry.date <= end_date, \
                            Entry.insom_type == insom_type).\
                            group_by(Entry.insom_type).all()

    if len(frequency_type) != 0:
        return frequency_type[0][1]
    else:
        return 0



# NOTE: Complete return statements during Phase 3 refactor.
def most_frequent_type_text(insom_type):
    """Returns text that accompanies the most_frequent_insom_type insight."""

    if insom_type == 'early-awakening':
        return "Early-awakening insomnia has a variety of causes, including \
        inconsistent bedtimes, depression, low blood sugar, and hormonal \
        imbalances. Talk to your doctor about triggers of your \
        early-awakening insomnia."
    elif insom_type == 'sleep-maintenance':
        return "sleep main"
    elif insom_type == 'sleep-onset':
        return "sleep ons"


# NOTE: Rename to more intuitive name during Phase 3 refactor.
def integer_type_data(user_id, start_date, end_date, column_name):
    """Returns a tuple of lists, one list of dates as strings, and one list of 
    data points as integers. column_name should be an object with attribute
    column_name, e.g. Entry.stress_level."""

    data_points = sorted(db.session.query(Entry.date, column_name).filter\
        (Entry.user_id == user_id, Entry.date >= start_date, 
        Entry.date <= end_date).all())

    dates = []
    scores = []
    
    for item in data_points:
        date = "%s/%s" % (item[0].month, item[0].day)
        dates.append(date)

        score = item[1]
        scores.append(score)

    return dates, scores



def hours_sleep_data(user_id, start_date, end_date):
    """Returns a tuple of lists, one list of dates as strings,
    and one list of hours_sleep data points as integers."""

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



def insom_factors(user_id, column_name):
    """Returns the percentage co-occurrence between insomnia(T/F) 
    and another column with T/F values. column_name should be a table object
    with attribute column_name."""

    query_list = db.session.query(Entry.insomnia, column_name).filter\
    (Entry.user_id == user_id).order_by('date').all()

    insom_list = []
    mens_list = []

    for item in query_list:
        insom_list.append(item[0])
        mens_list.append(item[1])

    co_occurrence = calculate_similarity(insom_list, mens_list)

    return co_occurrence



def strongest_insom_factor(user_id, start_date, end_date):
    """Returns the insom_factor with the highest correlation 
    with insom_severity. """

    alcohol_factor = insom_factors(user_id, Entry.alcohol)
    caffeine_factor = insom_factors(user_id, Entry.caffeine)
    mens_factor = insom_factors(user_id, Entry.menstruation)

    factors = {
                "Alcohol": alcohol_factor,
                "Caffeine": caffeine_factor,
                "Menstruation": mens_factor
                }
 
    insom_factor = key_of_largest_value(factors)

    return insom_factor



def insom_factor_text(user_id, start_date, end_date):
    """Returns text that accompanies the strongest_insom_factor."""

    insom_factor = strongest_insom_factor(user_id, start_date, end_date)

    if insom_factor == "Alcohol":
        return "Have you noticed that alcohol impacts your sleep? Based on the \
        data you've provided, there's a strong correlation between insomnia and \
        drinking alcohol. Try giving up alcohol for 4 weeks, log your sleep, \
        and see if your insomnia improves."
    elif insom_factor == "Caffeine":
        return "Have you noticed that caffeine impacts your sleep? Based on the \
        data you've provided, there's a strong correlation between insomnia and \
        consuming caffeine. Try giving up caffeine for 4 weeks, log your sleep, \
        and see if your insomnia improves."
    elif insom_factor == "Menstruation":
        return "Have you noticed that your insomnia gets worse during your \
        period? If so, you may have a hormonal imbalance. Talk to your doctor \
        about treatments for hormonal insomnia."



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
