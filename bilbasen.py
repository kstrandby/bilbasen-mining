# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 14:49:50 2014

@author: kristine
"""
from __future__ import unicode_literals
import httplib
from bs4 import BeautifulSoup
import time
import MySQLdb as mdb
import sys
from collections import namedtuple
""" 
eksempel på query:
Mærke: Ford, Model: Ka, Fra år: 2010
/brugt/bil/ford/ka?Fuel=0&KmlFrom=0&YearFrom=2010&PriceFrom=0&PriceTo=10000000&MileageTo=0
&ZipCode=0000&IncludeEngrosCVR=True&IncludeSellForCustomer=True&IncludeWithoutVehicleRegistrationTax=True
&IncludeLeasing=False&HpFrom=&HpTo=
"""


# define convenient tuple to use for car
Car = namedtuple('Car', 'model link description kms year hk kml kmt moth trailer location price')

# function to extract car information from html listing
def extractCarInfo(listing_type, listing):
    model = listing.find('a', attrs={'class': 'listing-heading darkLink'}).string
    link = listing.find('a', attrs={'class': 'listing-heading darkLink'})['href']
    
    if listing_type == 'plus' or listing_type == 'discount':
        description = listing.find('div', class_='listing-description expandable-box').string
        description = description.replace("'", "''")
    elif listing_type == 'exclusive':
        description = listing.find('div', class_='row exclusive-listing-description').string
        description = description.replace("'", "''")
 
    data = listing.find_all('div', class_='col-xs-2 listing-data ')
    kms = data[1].string
    year = data[2].string
    vardata = listing.find('span', class_='variableDataColumn')
    hk = vardata['data-hk']
    kml = vardata['data-kml']
    kmt = vardata['data-kmt']
    moth = vardata['data-moth']
    trailer = vardata['data-trailer']
    pricestr = listing.find('div', class_='col-xs-3 listing-price ').string
    pricestr = pricestr.replace('Kr', '')
    pricestr = pricestr.replace('.', '')
    pricestr = pricestr.replace('Ring', '0')
    price = int(pricestr)
    location = listing.find('div', class_='col-xs-2 listing-region ').string
    
    car = Car(model, link, description, kms, year, hk, kml, kmt, moth, trailer, location, price)
    return car

# function to check for the existence of a table in a database
def checkIfTableExist(cursor, tableName):
    stmt = "SHOW TABLES LIKE 'tableName'"
    cursor.execute(stmt)
    result = cursor.fetchone()
    if result:
        return True
    else:
        return False

# function to get the current date
def getDate():
     t = time.strftime("%d%m%y")
     return t
 
# function to extract car brands from bilbasen.dk
def getCarBrands(conn):
    conn.request("GET", "/")
    res = conn.getresponse()
    content = res.read()
    parsed_html = BeautifulSoup(content)

    # extract car brands
    brands_tags = parsed_html.find("optgroup", {"label": "Alle mærker"})
    brands = []
    for child in brands_tags.children:
        brands.append(child.string)
    return brands


# function to create connection to bilbasen.dk
# @return the response
def connect():
    return httplib.HTTPConnection("www.bilbasen.dk")
    

def downloadDataToDatabase():
    Brand = "" # add forwardslash e.g. "/ford"
    Model = "" # add forwardslash e.g. "/ka"
    Fuel = "0"
    Kmlfrom = "0"
    Fromyear = "0"
    Pricefrom = "0"
    Priceto = "10000000"
    Mileageto= "0"
    Zipcode = "0000"
    IncludeEngrosCVR = "True"
    IncludeSellForCustomer = "True"
    IncludeWithoutVehicleRegistrationTax = "True"
    IncludeLeasing = "False"
    HpFrom = ""
    HpTo = ""
    page="1"


    query = "/brugt/bil"+Brand+Model+"?Fuel="+Fuel+"&KmlFrom="+Kmlfrom+"&YearFrom="+Fromyear+"&PriceFrom="+Pricefrom+"&PriceTo="\
        +Priceto+"&MileageTo="+Mileageto+"&ZipCode="+Zipcode+"&IncludeEngrosCVR="+IncludeEngrosCVR+"&IncludeSellForCustomer="\
        +IncludeSellForCustomer+"&IncludeWithoutVehicleRegistrationTax="+IncludeWithoutVehicleRegistrationTax+"&IncludeLeasing="\
        +IncludeLeasing+"&HpFrom="+HpFrom+"&HpTo="+HpTo+"&page="+page

    conn = connect()
    conn.request("GET", query)
    res = conn.getresponse()

    content = res.read()
    parsed_html = BeautifulSoup(content)


    # connect to database
    con = None
    try:
        con = mdb.connect('localhost', 'user', 'bilbasen', 'bilbasendb');
        con.set_character_set('utf8')
        cur = con.cursor()
        cur.execute('SET NAMES utf8;') 
        cur.execute('SET CHARACTER SET utf8;')
        cur.execute('SET character_set_connection=utf8;')
    

        with con:
        
            date = getDate()
            tablename = 'AllCars' + date
            command = "CREATE TABLE " + tablename + "(Link CHAR(100), Model CHAR(100), Description MEDIUMTEXT, Kms INT(20), Year INT(4), \
                    Kml CHAR(20), Kmt CHAR(20), Moth CHAR(30), Trailer CHAR(30), Location CHAR(50), Price INT(20))"
            cur.execute(command)
       

            npages = None
            # extract total number of pages to crawl
            uls=parsed_html.find('ul', {'class': 'pagination pull-right'})
            count = 0
            lis = uls.find_all('li')
            for li in lis:
                if li.text == '...':
                    npagesstring = lis[count+1].text
                    npages = int(npagesstring.replace('.',''))
                count+=1
        
            print "pages to crawl: %s" %npages
    
            # go through all pages of search result
            while int(page) <= npages:
    
                print "crawling page " + page
                # extract all cars and links to detailed page

            
                rllplus = parsed_html.find_all('div', attrs={'class': 'row listing listing-plus'})
                rllexclusive = parsed_html.find_all('div', attrs={'class': 'row listing listing-exclusive'})
                rlldiscount = parsed_html.find_all('div', attrs={'class': 'row listing listing-discount'})
                
                for listing in rllplus:        
                    car = extractCarInfo('plus', listing)
                    cur.execute("INSERT INTO "+tablename+"(Link, Model, Description, Kms, Year, Kml, Kmt, Moth, Trailer, Location, Price) \
                        VALUES('%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                        %(getattr(car, 'model'), getattr(car, 'link'), getattr(car, 'description'), getattr(car, 'kms'), \
                        getattr(car, 'year'), getattr(car, 'kml'), getattr(car, 'kmt'), getattr(car, 'moth'), \
                        getattr(car, 'trailer'), getattr(car, 'location'), getattr(car, 'price')))

                for listing in rllexclusive:
                    car = extractCarInfo('exclusive', listing)
                    cur.execute("INSERT INTO "+tablename+"(Link, Model, Description, Kms, Year, Kml, Kmt, Moth, Trailer, Location, Price) \
                        VALUES('%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                        %(getattr(car, 'model'), getattr(car, 'link'), getattr(car, 'description'), getattr(car, 'kms'), \
                        getattr(car, 'year'), getattr(car, 'kml'), getattr(car, 'kmt'), getattr(car, 'moth'), \
                        getattr(car, 'trailer'), getattr(car, 'location'), getattr(car, 'price')))
                    
                for listing in rlldiscount:        
                    car = extractCarInfo('discount', listing)
                    cur.execute("INSERT INTO "+tablename+"(Link, Model, Description, Kms, Year, Kml, Kmt, Moth, Trailer, Location, Price) \
                        VALUES('%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                        %(getattr(car, 'model'), getattr(car, 'link'), getattr(car, 'description'), getattr(car, 'kms'), \
                        getattr(car, 'year'), getattr(car, 'kml'), getattr(car, 'kmt'), getattr(car, 'moth'), \
                        getattr(car, 'trailer'), getattr(car, 'location'), getattr(car, 'price')))
                
    
                incr = int(page) 
                incr +=1
                page = str(incr)
            
                query = "/brugt/bil"+Brand+Model+"?Fuel="+Fuel+"&KmlFrom="+Kmlfrom+"&YearFrom="+Fromyear+"&PriceFrom="\
                    +Pricefrom+"&PriceTo="+Priceto+"&MileageTo="+Mileageto+"&ZipCode="+Zipcode+"&IncludeEngrosCVR="\
                    +IncludeEngrosCVR+"&IncludeSellForCustomer="+IncludeSellForCustomer+"&IncludeWithoutVehicleRegistrationTax="\
                    +IncludeWithoutVehicleRegistrationTax+"&IncludeLeasing="+IncludeLeasing+"&HpFrom="+HpFrom+"&HpTo="+HpTo+"&page="+page

                conn.request("GET", query)
                res = conn.getresponse()
                content = res.read()
                parsed_html = BeautifulSoup(content)


    # in case of database error
    except mdb.Error, e:
  
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)

    # close connection to database
    if con:  
        cur.close()
        con.commit()
        con.close() 
    

    

