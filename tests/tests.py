# -*- coding: utf-8 -*-

import unittest
import pandas

import database
import datamining


class Testdatamining(unittest.TestCase):
    """ TestCase testing functions of the datamining module """

    def setUp(self):
        """ sets up testing data by calling the initalize function """
        database.createTestTable()

    def test_extractBrands(self):
        """ tests the test_extractBrands function of the datamining module """
        brands = ['Audi A8', 'Ford Ka', 'BMW X6', 'Renault Clio', 'Fiat 500',
                  'Honda Civic']
        expected = ['Audi', 'Ford', 'BMW', 'Renault', 'Fiat', 'Honda']
        result = datamining.extractBrands(brands)
        self.assertListEqual(expected, result)

    def test_getDistributionAllBrands(self):
        """ tests the getDistributionAllBrands function of the datamining
            module """
        result = datamining.getDistributionAllBrands('testTable')
        expected = pandas.DataFrame.from_records(
            [['Audi', 3, '60.00%'], ['Ford', 1, '20.00%'],
             ['Mercedes', 1, '20.00%']],
            columns=['Brand', 'Number', 'Percentage'])
        pandas.util.testing.assert_frame_equal(expected, result)

    def test_getDistributionOneBrand(self):
        """ tests the getDistributionOneBrand function of the datamining
            module """
        result = datamining.getDistributionOneBrand('testTable', 'Audi')
        expected = pandas.DataFrame.from_records(
            [['Audi A1', 1, '33.33%'], ['Audi A2', 1, '33.33%'],
             ['Audi A3', 1, '33.33%']],
            columns=['Model', 'Number', 'Percentage'])
        pandas.util.testing.assert_frame_equal(expected, result)

    def test_getLocationDistributionOneBrand(self):
        """ tests the getLocationDistributionOneBrand function of the
            datamining module """
        result = datamining.getLocationDistributionOneBrand(
            'testTable', 'Audi')
        expected = pandas.Series(
            [1, 1, 1, 0],
            index=['Sjælland', 'Fyn', 'Bornholm', 'Jylland'])
        pandas.util.testing.assert_series_equal(expected, result)

    def test_getLocationDistributionAllBrands(self):
        """ tests the getDistributionAllBrands function of the datamining
            module """
        result = datamining.getLocationDistributionAllBrands('testTable')
        expected = pandas.Series(
            [1, 2, 1, 1],
            index=['Sjælland', 'Fyn', 'Bornholm', 'Jylland'])
        pandas.util.testing.assert_series_equal(expected, result)

    def test_getMostExpensiveCars(self):
        """ tests the getMostExpensiveCars function of the datamining
            module """
        result = datamining.getMostExpensiveCars('testTable')
        expected = pandas.DataFrame(['Mercedes SLK'], index=['Model'])
        pandas.util.testing.assert_series_equal(expected.T.Model, result.Model)

    def test_getCheapestCars(self):
        """ tests the getCheapestCars function of the datamining module """
        result = datamining. getCheapestCars('testTable')
        expected = pandas.DataFrame(['Ford Mondeo'], index=['Model'])
        pandas.util.testing.assert_series_equal(expected.T.Model, result.Model)

    def test_getFastestCars(self):
        """ tests the getFastestCars function of the datamining module """
        result = datamining.getFastestCars('testTable')
        expected = pandas.DataFrame(['Mercedes SLK'], index=['Model'])
        pandas.util.testing.assert_series_equal(expected.T.Model, result.Model)

    def test_getMostEcofriendlyCars(self):
        """ tests the getMostEcofriendlyCars function of the datamining
            module """
        result = datamining.getMostEcofriendlyCars('testTable')
        expected = pandas.DataFrame(['Ford Mondeo'], index=['Model'])
        pandas.util.testing.assert_series_equal(expected.T.Model, result.Model)


class TestDatabase(unittest.TestCase):
    """ TestCase testing functions of the database module """

    def setUp(self):
        """ sets up a "fake" newest table to test on """
        cur, con = database.connectToDatabase()
        database.query(
            cur, "CREATE TABLE AllCars010115(Column1 INT, Column2 INT)")

    def tearDown(self):
        """ deletes the "fake" table to clean up the database """
        cur, con = database.connectToDatabase()
        database.query(cur, "DROP TABLE AllCars010115")

    def test_checkIfTableExist(self):
        """ tests the checkIfTableExist function of the database module """
        cur, con = database.connectToDatabase()
        # test that false is returned when checking for a non-existing table
        result = database.checkIfTableExist(cur, "test")
        self.assertFalse(result)

        # test that the fake table exist
        result = database.checkIfTableExist(cur, "AllCars010115")
        self.assertTrue(result)

    def test_getNewestTable(self):
        """ tests the getNewestTable function of the database module """
        result = database.getNewestTable()
        self.assertEquals("AllCars010115", result)

    def test_getCarBrands(self):
        """ tests the getCarBrands function of the bilbasen module """
        expected = pandas.Series(
            [(u'AMC'), (u'Abarth'), (u'Afuture'), (u'Alfa Romeo'), (u'Alpina'),
             (u'Aston Martin'), (u'Audi'), (u'Austin'), (u'Austin Healey'),
             (u'Autobianchi'), (u'BMW'), (u'Bentley'), (u'Buick'),
             (u'Cadillac'), (u'Charron'), (u'Chevrolet'), (u'Chrysler'),
             (u'Citroën'), (u'Corvette'), (u'DKW'), (u'Dacia'), (u'Daewoo'),
             (u'Daihatsu'), (u'Daimler'), (u'Datsun'), (u'DeTomaso'),
             (u'Dodge'), (u'Excalibur'), (u'Ferrari'), (u'Fiat'), (u'Ford'),
             (u'GMC'), (u'Honda'), (u'Hummer'), (u'Hyosung'), (u'Hyundai'),
             (u'Infiniti'), (u'Isuzu'), (u'Jaguar'), (u'Jeep'), (u'Kewet'),
             (u'Kia'), (u'Kinroad'), (u'Lada'), (u'Lamborghini'), (u'Lancia'),
             (u'Land Rover'), (u'Lexus'), (u'Lincoln'),
             (u'London Taxis International'), (u'Lotus'), (u'MG'),
             (u'Maserati'), (u'Mazda'), (u'Mercedes'), (u'Mercury'), (u'Mini'),
             (u'Mitsubishi'), (u'Morgan'), (u'Morris'), (u'NSU'), (u'Nissan'),
             (u'Oldsmobile'), (u'Opel'), (u'Peugeot'), (u'Plymouth'),
             (u'Pontiac'), (u'Porsche'), (u'Reliant'), (u'Renault'), (u'Reva'),
             (u'Rolls Royce'), (u'Rover'), (u'Saab'), (u'Seat'), (u'Skoda'),
             (u'Smart'), (u'Ssangyong'), (u'Subaru'), (u'Sunbeam'),
             (u'Suzuki'), (u'Tata'), (u'Tesla'), (u'Think'), (u'Toyota'),
             (u'Trabant'), (u'Triumph'), (u'VW'), (u'Vauxhall'), (u'Volvo'),
             (u'Willys')])
        result = database.getCarBrands()
        pandas.util.testing.assert_series_equal(expected, result)

    def test_getLocations(self):
        """ """

if __name__ == '__main__':
    unittest.main()
