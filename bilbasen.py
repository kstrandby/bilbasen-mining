# -*- coding: utf-8 -*-
"""
Bilbasen module
This module handles all communication with bilbasen.dk, and it thus contains functions to communicate with bilbasen.dk
as well as functions to download data from bilbasen.dk.
"""
from bs4 import BeautifulSoup
from collections import namedtuple
import httplib
import database
import time
import MySQLdb as mdb


# define convenient tuple to use for car
Car = namedtuple('Car', 'model link description kms year hk kml kmt moth trailer location price')

def connect():
	""" returns a httplib connection to bilbasen.dk """
	return httplib.HTTPConnection("www.bilbasen.dk")

# function to extract car information from html listing
def extractCarInfo(listing_type, listing):
    model = listing.find('a', attrs={'class': 'listing-heading darkLink'}).string
    model = model.encode('utf8')
    link = listing.find('a', attrs={'class': 'listing-heading darkLink'})['href']
    
    if listing_type == 'plus' or listing_type == 'discount':
        description = listing.find('div', class_='listing-description expandable-box').string
        description = description.replace("'", "''")
        description = smart_str(description)
    elif listing_type == 'exclusive':
        description = listing.find('div', class_='row exclusive-listing-description').string
        description = description.replace("'", "''")
        description = smart_str(description)
 
    data = listing.find_all('div', class_='col-xs-2 listing-data ')
    kmsstr = data[1].string
    kmsstr = kmsstr.replace(".", "")
    kms = int(kmsstr)
    year = data[2].string
    vardata = listing.find('span', class_='variableDataColumn')
    hk = vardata['data-hk']
    kml = vardata['data-kml']
    kml = kml.replace("km/l", "")
    kml = kml.replace(",", ".")
    kml = kml.replace("-", "")
    if kml == "": # no information given
        kml = None
    else:
        kml = Decimal(kml)
    kmt = vardata['data-kmt']
    kmt = kmt.replace("sek.", "")
    kmt = kmt.replace(",", ".")
    kmt = kmt.replace("-", "")
    if kmt == "": # no information given
        kmt = None
    else:
        kmt = Decimal(kmt)
    
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

# function to get the current date
def getDate():
     t = time.strftime("%d%m%y")
     return t
 
# function to extract car brands from bilbasen.dk and put them into a database
def downloadCarBrandsToDatabase(conn):
    conn.request("GET", "/")
    res = conn.getresponse()
    content = res.read()
    parsed_html = BeautifulSoup(content, from_encoding='utf8')
    con = mdb.connect('localhost', 'user', 'bilbasen', 'bilbasendb', charset='utf8')
    cur = con.cursor()
    cur.execute("SET character_set_client = utf8")

    if not checkIfTableExist(cur, 'Brands'):
        cur.execute("CREATE TABLE Brands(Brand CHAR(100))")
    # extract car brands
    brands_tags = parsed_html.find("optgroup", {"label": "Alle mærker"})
    print brands_tags
    for child in brands_tags.children:
        brand = smart_str(child.string)
        if any(c.isalpha() for c in brand):
            command = "INSERT INTO Brands(Brand) VALUES('%s')" %str(brand)
            print len(command)
            print command
            cur.execute(command)
    cur.close()
    con.commit()
    con.close()

def downloadDataToDatabase(limit = None):
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
        # kms er kilometer kørt, kms er 0-100 km/t
            date = getDate()
            tablename = 'AllCars' + date
            command = "CREATE TABLE " + tablename + "(Model CHAR(100), Link CHAR(100), Description MEDIUMTEXT, Kms INT(20), Year INT(4), \
                    Kml FLOAT(50), Kmt FLOAT(50), Moth CHAR(30), Trailer CHAR(30), Location CHAR(50), Price INT(20))"
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
        

    
            # go through all pages of search result
            if limit == None: 
                limit = npages
            print "pages to crawl: %s" %limit
                
            while int(page) <= limit:
    
                print "crawling page " + page
                # extract all cars and links to detailed page

            
                rllplus = parsed_html.find_all('div', attrs={'class': 'row listing listing-plus'})
                rllexclusive = parsed_html.find_all('div', attrs={'class': 'row listing listing-exclusive'})
                rlldiscount = parsed_html.find_all('div', attrs={'class': 'row listing listing-discount'})
                
                for listing in rllplus:   
                    car = extractCarInfo('plus', listing)
                    cur.execute("INSERT INTO "+tablename+"(Model, Link,  Description, Kms, Year, Kml, Kmt, Moth, Trailer, Location, Price) \
                        VALUES('%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                        %(str(getattr(car, 'model')), getattr(car, 'link'), getattr(car, 'description'), getattr(car, 'kms'), \
                        getattr(car, 'year'), getattr(car, 'kml'), getattr(car, 'kmt'), getattr(car, 'moth'), \
                        getattr(car, 'trailer'), smart_str(getattr(car, 'location')), getattr(car, 'price')))

                for listing in rllexclusive:
                    car = extractCarInfo('exclusive', listing)
                    cur.execute("INSERT INTO "+tablename+"(Model, Link, Description, Kms, Year, Kml, Kmt, Moth, Trailer, Location, Price) \
                        VALUES('%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                        %(str(getattr(car, 'model')), getattr(car, 'link'), getattr(car, 'description'), getattr(car, 'kms'), \
                        getattr(car, 'year'), getattr(car, 'kml'), getattr(car, 'kmt'), getattr(car, 'moth'), \
                        getattr(car, 'trailer'), smart_str(getattr(car, 'location')), getattr(car, 'price')))
                    
                for listing in rlldiscount:        
                    car = extractCarInfo('discount', listing)
                    cur.execute("INSERT INTO "+tablename+"(Model, Link, Description, Kms, Year, Kml, Kmt, Moth, Trailer, Location, Price) \
                        VALUES('%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                        %(str(getattr(car, 'model')), getattr(car, 'link'), getattr(car, 'description'), getattr(car, 'kms'), \
                        getattr(car, 'year'), getattr(car, 'kml'), getattr(car, 'kmt'), getattr(car, 'moth'), \
                        getattr(car, 'trailer'), smart_str(getattr(car, 'location')), getattr(car, 'price')))
                
    
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
        commitToDatabase(cur, con)