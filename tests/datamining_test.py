# -*- coding: utf-8 -*-
""" This module tests the datamining module. """
from __future__ import division
import unittest
import pandas
from decimal import *
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', '')))
import datamining
import database


class TestDatamining(unittest.TestCase):

    """ TestCase testing functions of the datamining module. """

    def setUp(self):
        """ Set up testing data. """
        create_test_table()

    def test_get_distribution_all_brands(self):
        """ Test the get_distribution_all_brands function.

        This test also indirectly tests the create_distribution
        function, as this is used in the get_distribution_all_brands
        function.
        """
        result = datamining.get_distribution_all_brands('testTable')
        expected = pandas.DataFrame.from_records(
            [['Audi', 3, '60.00%'], ['Ford', 1, '20.00%'],
             ['Mercedes', 1, '20.00%']],
            columns=['Brand', 'Number', 'Percentage'])
        pandas.util.testing.assert_frame_equal(expected, result)

    def test_get_distribution_one_brand(self):
        """ Test the get_distribution_one_brand function. """
        result = datamining.get_distribution_one_brand('testTable', 'Audi')
        expected = pandas.DataFrame.from_records(
            [['Audi A1', 1, '33.33%'], ['Audi A2', 1, '33.33%'],
             ['Audi A3', 1, '33.33%']],
            columns=['Model', 'Number', 'Percentage'])
        pandas.util.testing.assert_frame_equal(expected, result)
        # test when the model is not present (error condition)
        result = datamining.get_distribution_one_brand('testTable', 'Ferrari')
        self.assertListEqual([], result)

    def test_get_location_distribution_one_brand(self):
        """ Test the get_location_distribution_one_brand function. """
        result = datamining.get_location_distribution_one_brand(
            'testTable', 'Audi')
        expected = pandas.Series(
            [1, 1, 1, 0],
            index=['Sjælland', 'Fyn', 'Bornholm', 'Jylland'])
        pandas.util.testing.assert_series_equal(expected, result)

    def test_get_location_distribution_all_brands(self):
        """ Test the get_distribution_all_brands function. """
        result = datamining.get_location_distribution_all_brands('testTable')
        expected = pandas.Series(
            [1, 2, 1, 1],
            index=['Sjælland', 'Fyn', 'Bornholm', 'Jylland'])
        pandas.util.testing.assert_series_equal(expected, result)

    def test_extract_brands(self):
        """ Test the test_extract_brands function. """
        brands = ['Audi A8', 'Ford Ka', 'BMW X6', 'Renault Clio', 'Fiat 500',
                  'Honda Civic']
        expected = ['Audi', 'Ford', 'BMW', 'Renault', 'Fiat', 'Honda']
        result = datamining.extract_brands(brands)
        self.assertListEqual(expected, result)

    def test_get_most_expensive_cars(self):
        """ Test the get_most_expensive_cars function. """
        result = datamining.get_most_expensive_cars('testTable')
        expected = pandas.DataFrame(['Mercedes SLK'], index=['Model'])
        pandas.util.testing.assert_series_equal(expected.T.Model, result.Model)

    def test_get_cheapest_cars(self):
        """ Test the get_cheapest_cars function. """
        result = datamining. get_cheapest_cars('testTable')
        expected = pandas.DataFrame(['Ford Mondeo'], index=['Model'])
        pandas.util.testing.assert_series_equal(expected.T.Model, result.Model)

    def test_get_fastest_cars(self):
        """ Test the get_fastest_cars function. """
        result = datamining.get_fastest_cars('testTable')
        expected = pandas.DataFrame(['Mercedes SLK'], index=['Model'])
        pandas.util.testing.assert_series_equal(expected.T.Model, result.Model)

    def test_get_most_ecofriendly_cars(self):
        """ Test the get_most_ecofriendly_cars function. """
        result = datamining.get_most_ecofriendly_cars('testTable')
        expected = pandas.DataFrame(['Ford Mondeo'], index=['Model'])
        pandas.util.testing.assert_series_equal(expected.T.Model, result.Model)

    def test_simplify_model_names(self):
        """ Test the simplify_model_names function. """
        model = ['Audi A5 2.0 4d']
        expected = ['Audi A5']
        result = datamining.simplify_model_names(model)
        self.assertEquals(expected, result)

    def test_analyze_description(self):
        """ Test the analyze_description function. """
        pos_description = u"""attraktiv, nysynet og topudstyret bil med abs,
            esp, og servo"""
        # it contains 6 words in our positive word list and 10 in total
        expected = 6/10
        result = datamining.analyze_description(pos_description)
        self.assertEquals(expected, result)

        neg_description = u"""nyserviceret bil med en smule rust og en lille
            bule i føredøren."""
        # 1 pos word and 2 neg words, 12 in total
        expected = (1-(2*2))/12
        result = datamining.analyze_description(neg_description)
        self.assertEquals(expected, result)

        no_description = ""
        result = datamining.analyze_description(no_description)
        self.assertEquals(0, result)


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
