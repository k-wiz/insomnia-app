import server
from server import app
import unittest
from unittest import TestCase
from helper import *
from datetime import datetime, date
from model import connect_to_db, db, User, Entry, example_data


class MyAppUnitTestCase(unittest.TestCase):
    """Unit tests: discrete code testing."""

    def test_convert_to_boolean(self):
        self.assertEqual(convert_to_boolean('False'), False)
        self.assertEqual(convert_to_boolean('True'), True)

    def test_median(self):
        self.assertEqual(median([1,1,2,5,6,6,9]), 5)
        self.assertEqual(median([1,1,2,6,6,9]), 4)
        self.assertEqual(median([]), None)


    def test_calculate_similarity(self):
        self.assertEqual(calculate_similarity([1,1,1], [1,1,1]), 1.0)
        self.assertEqual(calculate_similarity([1,1,1,1], [1,1,1,2]), .75)



class FlaskTests(TestCase):
    """Flask & database tests"""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

        #Connect to test db
        connect_to_db(app, 'postgresql:///testdb')

        #Create tables & add sample data
        db.create_all()
        example_data()


    def tearDown(self):
        db.session.close()
        db.drop_all()


    # Tests for app routes. 
    def test_home(self):
        """Test root page."""
        
        result = self.client.get('/')
        self.assertIn('<h1>Log Your Sleep</h1>', result.data)


    def test_dashboard(self):
        """Test dashboard route."""

        test_client = server.app.test_client()
        result = test_client.post('/dashboard', data={'hours_sleep': '1', 
                                                        'insom_severity': '1',
                                                        'bedtime': '23:00',
                                                        'stress_level': '1',
                                                        'activity_level': '1'})
        self.assertIn('<div class="panel">', result.data)


    def test_entry(self):
        """Test entry route."""

        result = self.client.get('/entry')
        self.assertIn('<legend>How did you sleep last night?</legend>', result.data)


    def test_insom_types(self):
        """Test insom-types.json route."""

        result = self.client.get('/insom-types.json')
        self.assertIn("insom_type", result.data)



    #Tests for functions in helper.py that call the db. 
    def test_calculate_avg_sleep(self):
        self.assertEqual(calculate_avg_sleep('1', 
                                            datetime(2016,5,1), 
                                            datetime(2016,5,2)), 7.0)


    def test_calculate_avg_sleep_over_time(self):
        self.assertEqual(calculate_avg_sleep_over_time('1', 
                                            datetime(2016,5,1), 
                                            datetime(2016,5,8)), ([7.0], ['5/8']))



    def test_calculate_median_sleep(self):
        self.assertEqual(calculate_median_sleep('1', 
                                            datetime(2016,5,1), 
                                            datetime(2016,5,2)), 7.0)

   

    def test_first_entry(self):
        self.assertEqual(first_entry('1'), date(2016, 5, 1))



    def test_last_entry(self):
        self.assertEqual(last_entry('1'), date(2016, 5, 8))



    def test_frequency_insomnia_type(self):
        self.assertEqual(frequency_insomnia_type('1', 
                                            datetime(2016,5,1), 
                                            datetime(2016,5,2), 'x'), 0)




    def test_create_or_update_record(self):
        """Test if creating a record works."""

        self.assertEqual(create_or_update_record(user_id=1, 
                date=datetime(2016,5,5), 
                minutes_asleep=420, 
                insomnia=True,
                insom_type='early-awakening',
                insom_severity=1,
                alcohol=False,
                caffeine=True,
                menstruation=False,
                bedtime='23:00',
                stress_level=3,
                activity_level=4), None)


    def test_create_or_update_record(self):
        """Test if updating a record works."""

        user_id = 1
        date = datetime(2016,5,1)

        create_or_update_record(user_id=user_id, 
            date=date, 
            minutes_asleep=200, 
            insomnia=False,
            insom_type='early-awakening',
            insom_severity=7,
            alcohol=True,
            caffeine=False,
            menstruation=True,
            bedtime='23:30',
            stress_level=7,
            activity_level=2)

        entry = db.session.query(Entry.insom_severity).filter(Entry.user_id == user_id,
                                                            Entry.date == date).first()

        self.assertEqual(entry.insom_severity, 7)
        

    #WONT WORK. HOW DO I CORRECTLY REPRESENT OBJECT IF NOT IN A STRING?
    # def test_entry__repr__(self):

    #     new_entry = Entry(user_id=1, 
    #         date=datetime(2016,5,1), 
    #         minutes_asleep=200, 
    #         insomnia=False,
    #         insom_type='early-awakening',
    #         insom_severity=7,
    #         alcohol=True,
    #         caffeine=False,
    #         menstruation=True,
    #         bedtime='23:30',
    #         stress_level=7,
    #         activity_level=2)

    #     self.assertEqual(new_entry.insom_severity, 7)


    #WONT WORK. HOW DO I CORRECTLY REPRESENT OBJECT IF NOT IN A STRING? 
    # def test_user__repr__(self):

    #     new_user = User(user_id=1,
    #             age=30,
    #             gender='female',
    #             zipcode='94110',
    #             first_name='Kelli',
    #             email='kwisuri@gmail.com',
    #             password='booger')

    #     self.assertEqual(new_user.age, 30)



#####################################################

if __name__ == "__main__":
    unittest.main()