# -*- coding: utf-8 -*-

""" database module """

import MySQLdb as mdb
import pandas

def connectToDatabase():
	""" Returns a mysqldb cursor to the database """
	con = mdb.connect('localhost', 'user', 'bilbasen', 'bilbasendb', charset='utf8')
	cur = con.cursor()
	cur.execute("SET character_set_client = utf8")
	return cur, con

def checkIfTableExist(cursor, table):
	""" Checks if the specified table exist in the database """
	sql = "SHOW TABLES LIKE '" + table + "'"
	cursor.execute(sql)
	result = cursor.fetchone()
	if result:
		return True
	else:
		return False

def query(cursor, query):
	""" Executes the specified query and returns the retrieved data """
	cursor.execute(query)
	return cursor.fetchall()

def commit(cursor, connection):
	""" Commits any changes to the database - this function should be used after inserting and deleting """
	cursor.close()
	connection.commit()
	connection.close()

def getNewestTable():
	""" Returns the newest AllCars-table in the database by using the fact that the tables are named after
	the date they were generated (i.e. the date the data was download from bilbasen.dk) """
	cur, con = connectToDatabase()
	tables = pandas.read_sql_query("SHOW TABLES", con)
	newest = "0000000000000"

	for index,table in tables.iterrows():
		table = table['Tables_in_bilbasendb']
		if "AllCars" in str(table):
			table = str(table)

			newestday = int(newest[7] + newest[8])
			newestmonth = int(newest[9] + newest[10])
			newestyear = int(newest[11] + newest[12])

			day = int(table[7] + table[8])
			month = int(table[9] + table[10])
			year = int(table[11] + table[12])

			if year > newestyear:
				newest = table

			elif month > newestmonth and year == newestyear:
				newest = table

			elif day > newestday and month == newestmonth and year == newestyear:
				newest = table

	print "using table " + newest
	return newest

def getCarBrands():
	""" returns a pandas series of all the brands """
	cur, con = connectToDatabase()
	query = "SELECT * FROM Brands"
	result = pandas.read_sql_query(query, con)
	all_brands = result.Brand
	return all_brands

def getLocations(table):
	""" returns a pandas Series of all the sale locations present in the specified table """
	cur, con = connectToDatabase()
	query = "SELECT DISTINCT(location) FROM " + table + ";"
	result = pandas.read_sql_query(query, con)
	return result

def createTestTable():
    """ Creates a test table to have specific data to test on """
    cur, con = connectToDatabase()
    if not checkIfTableExist(cur, 'testTable'):
        sql = "CREATE TABLE testTable (Model CHAR(100), Link CHAR(100), Description MEDIUMTEXT, Kms INT(20), Year INT(4), \
                    Kml FLOAT(20), Kmt FLOAT(20), Moth CHAR(30), Trailer CHAR(30), Location CHAR(50), Price INT(20))"
        query(cur, sql)
        
        sql = "INSERT INTO testTable(Model, Link, Description, Kms, Year, Kml, Kmt, Moth, Trailer, Location, Price) \
                        VALUES('%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                        %('Audi A1', 'www.test.dk/audi1', 'Audi A1 description text', '100', '2000', '2', '6', '0', 'No trailer', 'Sjælland', '50000')
        query(cur, sql)
        sql = "INSERT INTO testTable(Model, Link, Description, Kms, Year, Kml, Kmt, Moth, Trailer, Location, Price) \
                        VALUES('%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                        %('Audi A2', 'www.test.dk/audi2', 'Audi A2 description text', '200', '2001', '3', '7', '0', 'No trailer', 'Fyn', '60000')
        query(cur, sql)
        sql = "INSERT INTO testTable(Model, Link, Description, Kms, Year, Kml, Kmt, Moth, Trailer, Location, Price) \
                        VALUES('%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                        %('Audi A3', 'www.test.dk/audi3', 'Audi A3 description text', '300', '2002', '4', '8', '0', 'No trailer', 'Bornholm', '70000')
        query(cur, sql)
        sql = "INSERT INTO testTable(Model, Link, Description, Kms, Year, Kml, Kmt, Moth, Trailer, Location, Price) \
                        VALUES('%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                        %('Ford Mondeo', 'www.test.dk/ford1', 'Ford Mondeo description text', '400', '2003', '5', '12', '0', 'No trailer', 'Jylland', '8000')
        query(cur, sql)
        sql = "INSERT INTO testTable(Model, Link, Description, Kms, Year, Kml, Kmt, Moth, Trailer, Location, Price) \
                        VALUES('%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                        %('Mercedes SLK', 'www.test.dk/mercedes1', 'Mercedes SLK description text', '500', '2004', '2', '4', '0', 'No trailer', 'Fyn', '100000')
    	query(cur, sql)
    	commit(cur, con)