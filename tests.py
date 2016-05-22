import server
import unittest
from unittest import TestCase
from server import app
from helper import *
from datetime import datetime, date
from model import connect_to_db, db, User, Entry, example_data


class MyAppUnitTestCase(unittest.TestCase):
    """Unit tests: discrete code testing."""

    def test_convert_to_boolean(self):
        self.assertEqual(convert_to_boolean('False'), False)

    def test_median(self):
        self.assertEqual(median([1,1,2,5,6,6,9]), 5)
        self.assertEqual(median([1,1,2,6,6,9]), 4)


    def test_calculate_similarity(self):
        self.assertEqual(calculate_similarity([1,1,1], [1,1,1]), 1.0)
        self.assertEqual(calculate_similarity([1,1,1,1], [1,1,1,2]), .75)



# class MyAppIntegrationTestCase(unittest.TestCase):
#     """Integration tests: testing Flask server."""

#     def setUp(self):
#         print "(setUp ran)"
#         self.client = server.app.test_client()
#         server.app.config['TESTING'] = True
#         server.app.config['DEBUG'] = False

#     def tearDown(self):
#         print "(tearDown ran)"

#     def test_home(self):
#         result = self.client.get('/')
#         self.assertIn('<h1>How did you sleep last night?</h1>', result.data)




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
        self.assertIn('<h1>How did you sleep last night?</h1>', result.data)


    def test_dashboard(self):
        """Test dashboard route."""

        test_client = server.app.test_client()
        result = test_client.post('/dashboard', data={'hours_sleep': '1', 
                                                        'insom_severity': '1',
                                                        'bedtime': '23:00',
                                                        'stress_level': '1',
                                                        'activity_level': '1'})
        self.assertIn('<div class="sleep-chart">', result.data)


    def test_insom_types(self):
        """Test insom-types.json route."""

        result = self.client.get('/insom-types.json')
        self.assertIn("insom_type", result.data)


    def test_insom_severity(self):
        """Test insom-severity.json route."""

        result = self.client.get('/insom-severity.json')
        self.assertIn("labels", result.data)


    #Tests for functions in helper.py that call the db. 
    def test_calculate_avg_sleep(self):
        self.assertEqual(calculate_avg_sleep('1', 
                                            datetime(2016,5,1), 
                                            datetime(2016,5,2)), 7.0)


    def test_calculate_avg_insom_severity(self):
        self.assertEqual(calculate_avg_insom_severity('1', 
                                            datetime(2016,5,1), 
                                            datetime(2016,5,2)), 1.0)


    def test_calculate_median_sleep(self):
        self.assertEqual(calculate_median_sleep('1', 
                                            datetime(2016,5,1), 
                                            datetime(2016,5,2)), 7.0)


    def test_calculate_median_insom_severity(self):
        self.assertEqual(calculate_median_insom_severity('1', 
                                            datetime(2016,5,1), 
                                            datetime(2016,5,2)), 1.0)


    def test_insom_type_frequency(self):
        self.assertEqual(insom_type_frequency('1', 
                                                datetime(2016,5,1), 
                                                datetime(2016,5,2)), 
                                                ([(u'early-awakening', 1L), 
                                                  (u'sleep-maintenance', 1L)]))


    def test_most_frequent_type(self):
        self.assertEqual(most_frequent_type('1', 
                                            datetime(2016,5,1), 
                                            datetime(2016,5,2)), 
                                            (1L, u'early-awakening'))


    def test_first_entry(self):
        self.assertEqual(first_entry('1'), date(2016, 5, 1))


    def test_last_entry(self):
        self.assertEqual(last_entry('1'), date(2016, 5, 4))


    def create_or_update_record(self):
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

        #How do I test lines 193-208? 
        self.assertEqual(create_or_update_record(user_id=1, 
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
                activity_level=4), None)




#####################################################

if __name__ == "__main__":
    unittest.main()