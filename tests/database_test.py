# -*- coding: utf-8 -*-
""" The module tests the database module. """

import unittest
import pandas
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', '')))
import database



class TestDatabase(unittest.TestCase):

    """ TestCase testing functions of the database module. """

    def setUp(self):
        """ Set up a "fake" newest table to test on. """
        cur, con = database.connect_to_database()
        database.query(
            cur, "CREATE TABLE AllCars010115(Column1 INT, Column2 INT)")

    def tearDown(self):
        """ Delete the "fake" table to clean up the database. """
        cur, con = database.connect_to_database()
        database.query(cur, "DROP TABLE AllCars010115")

    def test_check_if_table_exist(self):
        """ Test the check_if_table_exist function of the database module. """
        cur, con = database.connect_to_database()
        # test that false is returned when checking for a non-existing table
        result = database.check_if_table_exist(cur, "test")
        self.assertFalse(result)

        # test that the fake table exist
        result = database.check_if_table_exist(cur, "AllCars010115")
        self.assertTrue(result)

    def test_delete_table(self):
    	  """ Test the delete_table function of the database moule. """
    	  cur, con = database.connect_to_database()
    	  # delete the test table
    	  database.delete_table(cur, 'AllCars010115')
    	  # now check that it is gone
    	  result = database.check_if_table_exist(cur, 'AllCars010115')
    	  self.assertFalse(result)
    	  # create the table again for the rest of the tests
    	  self.setUp()

    def test_get_newest_table(self):
        """ Test the get_newest_table function of the database module. """
        result = database.get_newest_table()
        self.assertEquals("AllCars010115", result)

    def test_get_car_brands(self):
        """ Test the get_car_brands function of the database module. """
        result = database.get_car_brands()
        """ check that is returns something, as we cannot know what to
        expect it to contain """
        self.assertNotEqual(0, len(result))

    def test_get_locations(self):
        """ Test the get_locations function of the database module. """
        # create a test table (table with correct structure)
        create_test_table()
        result = database.get_locations('testTable')
        expected = pandas.DataFrame.from_records(
            [[u'Sjælland'], [u'Fyn'], [u'Bornholm'], [u'Jylland']],
            columns=['location'])
        pandas.util.testing.assert_frame_equal(expected, result)

    def test_car_exists(self):
        """ Test the car_exists function of the database module. """
        result = database.car_exists('Audi')
        self.assertTrue(result)
        result = database.car_exists('rubbish')
        self.assertFalse(result)


def create_test_table():
    """ Create a test table to have specific data to test on. """
    cur, con = database.connect_to_database()
    if not database.check_if_table_exist(cur, 'testTable'):
        sql = "CREATE TABLE testTable (Model CHAR(100), Link CHAR(100), \
        Description MEDIUMTEXT, Kms INT(20), Year INT(4), \
        Kml FLOAT(20), Kmt FLOAT(20), Moth CHAR(30), Trailer CHAR(30), \
        Location CHAR(50), Price INT(20))"
        database.query(cur, sql)

        sql = "INSERT INTO testTable(Model, Link, Description, Kms, Year, \
        Kml, Kmt, Moth, Trailer, Location, Price) VALUES('%s', '%s', '%s', \
        '%s','%s','%s','%s','%s','%s','%s','%s')" % (
            'Audi A1', 'www.test.dk/audi1', 'Audi A1 description text',
            '100', '2000', '2', '6', '0', 'No trailer', 'Sjælland', '50000')
        database.query(cur, sql)

        sql = "INSERT INTO testTable(Model, Link, Description, Kms, Year, \
        Kml, Kmt, Moth, Trailer, Location, Price) VALUES('%s', '%s', '%s', \
        '%s','%s','%s','%s','%s','%s','%s','%s')" % (
            'Audi A2', 'www.test.dk/audi2', 'Audi A2 description text',
            '200', '2001', '3', '7', '0', 'No trailer', 'Fyn', '60000')
        database.query(cur, sql)

        sql = "INSERT INTO testTable(Model, Link, Description, Kms, Year, \
        Kml, Kmt, Moth, Trailer, Location, Price) VALUES('%s', '%s', '%s', \
        '%s','%s','%s','%s','%s','%s','%s','%s')" % (
            'Audi A3', 'www.test.dk/audi3', 'Audi A3 description text',
            '300', '2002', '4', '8', '0', 'No trailer', 'Bornholm', '70000')
        database.query(cur, sql)

        sql = "INSERT INTO testTable(Model, Link, Description, Kms, Year, \
        Kml, Kmt, Moth, Trailer, Location, Price) VALUES('%s', '%s', '%s', \
        '%s','%s','%s','%s','%s','%s','%s','%s')" % (
            'Ford Mondeo', 'www.test.dk/ford1', 'Ford Mondeo description text',
            '400', '2003', '5', '12', '0', 'No trailer', 'Jylland', '8000')
        database.query(cur, sql)

        sql = "INSERT INTO testTable(Model, Link, Description, Kms, Year, \
        Kml, Kmt, Moth, Trailer, Location, Price) VALUES('%s', '%s', '%s', \
        '%s','%s','%s','%s','%s','%s','%s','%s')" % (
            'Mercedes SLK', 'www.test.dk/mercedes1',
            'Mercedes SLK description text',
            '500', '2004', '2', '4', '0', 'No trailer', 'Fyn', '100000')
        database.query(cur, sql)
        database.commit(cur, con)

if __name__ == '__main__':
    unittest.main()
