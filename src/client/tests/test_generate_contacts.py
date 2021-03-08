import unittest, datetime
from utils.generate_contacts import generate_unique_number, unique_numbers_array, dates_array


class TestGenerateContacts(unittest.TestCase):
    def test_generate_unique_number(self):
        numbers = [i for i in range(1000000000, 1000001000)]
        self.assertNotIn(generate_unique_number(numbers), numbers)

    def test_unique_numbers_array(self):
        unique_numbers = unique_numbers_array(amount=1000)
        length = len(unique_numbers)
        self.assertEqual(type(unique_numbers), list)
        self.assertEqual(length, 1000)
        for num in unique_numbers:
            self.assertEqual(unique_numbers.count(num), 1)

    def test_dates_array(self):
        dates = dates_array(amount=1000)
        length = len(dates)
        self.assertEqual(type(dates), list)
        self.assertEqual(length, 1000)
        for date in dates:
            self.assertEqual(dates.count(date), length)
            self.assertEqual(type(date), datetime.datetime)
