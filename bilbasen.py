# -*- coding: utf-8 -*-
"""
This module handles all communication with bilbasen.dk, and it
contains functions to communicate with bilbasen.dk as well as
functions to download data from bilbasen.dk.
The main part of the module runs the method download_data_to_database
which is the most important method of the module, as this is
where bilbasen.dk is crawled and the data is parsed and saved
in a database.
"""

from bs4 import BeautifulSoup
from collections import namedtuple
from django.utils.encoding import smart_str
from decimal import Decimal
import sys
import httplib
import time
import MySQLdb as mdb

import database


# define convenient tuple to use for car
Car = namedtuple('Car', 'model link description kms year hk kml kmt moth \
 trailer location price')


def connect():
    """ The method returns a httplib connection to bilbasen.dk. """
    return httplib.HTTPConnection("www.bilbasen.dk")


def extract_car_info(listing_type, listing):
    """ The method is used by the download_data_to_database().

    It and extracts data from a html listing. The data extracted is all the
    attributes on a car given on a search result site, which is:
    model, link to detailed page, description, how many km it has done,
    which year it is from, how many horsepowers it has, how many
    km per liter it does, how fast it goes from 0-100 km/t, what the
    monthly cost is, if it can pull a trailer, and a location.
    The method saves this data in the namedtupe Car and returns
    that tuple.
    """
    model = smart_str(listing.find(
        'a', attrs={'class': 'listing-heading darkLink'}).string)
    link = listing.find(
        'a', attrs={'class': 'listing-heading darkLink'})['href']

    """ an ad can be a 'plus', 'discount' or 'exclusive', and the
        class name of the div containing the description depends on
        this type. """
    if listing_type == 'plus' or listing_type == 'discount':
        description = listing.find(
            'div', class_='listing-description expandable-box').string
        if description is not None:
            description = description.replace("'", "''")
            description = smart_str(description)
    elif listing_type == 'exclusive':
        description = listing.find(
            'div', class_='row exclusive-listing-description').string
        if description is not None:
            description = description.replace("'", "''")
            description = smart_str(description)

    data = listing.find_all('div', class_='col-xs-2 listing-data ')
    kms = int(data[1].string.replace(".", ""))
    year = int(data[2].string)
    vardata = listing.find('span', class_='variableDataColumn')
    hk = vardata['data-hk']
    kml = vardata['data-kml'].replace("km/l", "") \
        .replace(",", ".").replace("-", "")
    if kml == "":  # no information given
        kml = None
    else:
        kml = Decimal(kml)
    kmt = vardata['data-kmt'].replace("sek.", "") \
        .replace(",", ".").replace("-", "")
    if kmt == "":  # no information given
        kmt = None
    else:
        kmt = Decimal(kmt)
    moth = smart_str(vardata['data-moth'])
    trailer = vardata['data-trailer']
    price = int(listing.find('div', class_='col-xs-3 listing-price ')
                .string.replace('Kr', '').replace('.', '')
                .replace('Ring', '0'))
    location = smart_str(listing.find(
        'div', class_='col-xs-2 listing-region ').string)

    car = Car(model, link, description, kms, year, hk, kml, kmt, moth,
              trailer, location, price)
    return car


def get_date():
    """ The method returns the current date. """
    t = time.strftime("%d%m%y")
    return t


def get_car_image_src(link):
    """ The method returns a link to an image of a car.

    Given a link to a car description page, a link to
    an image of the car is found and returned.
    """
    conn = connect()
    conn.request("GET",  link)
    res = conn.getresponse()
    content = res.read()
    parsed_html = BeautifulSoup(content, from_encoding='utf8')
    pics = parsed_html.find_all('a', {'id': 'bbVipGalleryLarge0'})
    src = ''
    for pic in pics:
        src = pic.find('img')['data-src']
    return src


def create_car_brand_table(conn):
    """ The method creates a database table of car brands.

    It crawls bilbasen.dk for a list of car brands, and creates
    and stores these brands in a table called 'Brands' in the
    database. The method is called each time the method
    download_data_to_database is called.
    """
    conn.request("GET", "/")
    res = conn.getresponse()
    content = res.read()
    parsed_html = BeautifulSoup(content, from_encoding='utf8')
    cur, con = database.connect_to_database()

    # delete the old table
    if database.check_if_table_exist(cur, 'Brands'):
        database.delete_table(cur, 'Brands')
        cur.execute("CREATE TABLE Brands(Brand CHAR(100))")

    # extract car brands and insert to database table
    brands_tags = parsed_html.find("optgroup", {"label": "Alle mærker"})
    for child in brands_tags.children:
        brand = smart_str(child.string)
        if any(c.isalpha() for c in brand):
            command = "INSERT INTO Brands(Brand) VALUES('%s')" \
                % smart_str(brand)
            cur.execute(command)
    database.commit(cur, con)


def insert_car_to_table(car, tablename, cursor):
    """ The method inserts a column with car data to a database table.

    This method takes as input a namedtuple Car, a name of a table
    in the database and a cursor to the database, and inserts the
    car into the given table.
    """
    cursor.execute("INSERT INTO "+tablename+"(Model, Link,  "
                   "Description, Kms, Year, Kml, Kmt, Moth, "
                   "Trailer, Location, Price) VALUES('%s', '%s', "
                   "'%s', '%s','%s','%s','%s','%s','%s','%s','%s')" %
                   (getattr(car, 'model'),
                    getattr(car, 'link'),
                    getattr(car, 'description'),
                    getattr(car, 'kms'),
                    getattr(car, 'year'),
                    getattr(car, 'kml'),
                    getattr(car, 'kmt'),
                    getattr(car, 'moth'),
                    getattr(car, 'trailer'),
                    getattr(car, 'location'),
                    getattr(car, 'price')))


def download_data_to_database(limit=None):
    """ The method scrapes data of cars at Bilbasen.dk.

    This method is the most important one of this module, as this is the
    one crawling bilbasen.dk to extract data of cars currently on sale.
    The method creates a new table each time it is called, and the table
    will be named 'AllBrandsDDMMYY', where DDMMYY is the current date. If
    the table already exist, it will be deleted.
    The method takes an optional parameter, defining how many pages to
    crawl. If no parameter is given, it crawls all pages (i.e. all cars)
    on bilbasen.dk.
    """
    # define the default parameters for the URI
    Brand = ""  # add forwardslash e.g. "/ford"
    Model = ""  # add forwardslash e.g. "/ka"
    Fuel = "0"
    Kmlfrom = "0"
    Fromyear = "0"
    Pricefrom = "0"
    Priceto = "10000000"
    Mileageto = "0"
    Zipcode = "0000"
    IncludeEngrosCVR = "True"
    IncludeSellForCustomer = "True"
    IncludeWithoutVehicleRegistrationTax = "True"
    IncludeLeasing = "False"
    HpFrom = ""
    HpTo = ""
    page = "1"

    # construct the URI
    query = "/brugt/bil" + Brand + Model + "?Fuel=" + Fuel + "&KmlFrom=" + \
        Kmlfrom + "&YearFrom=" + Fromyear + "&PriceFrom=" + Pricefrom + \
        "&PriceTo=" + Priceto + "&MileageTo=" + Mileageto + "&ZipCode=" + \
        Zipcode + "&IncludeEngrosCVR=" + IncludeEngrosCVR + \
        "&IncludeSellForCustomer=" + IncludeSellForCustomer + \
        "&IncludeWithoutVehicleRegistrationTax=" + \
        IncludeWithoutVehicleRegistrationTax + "&IncludeLeasing=" + \
        IncludeLeasing + "&HpFrom=" + HpFrom + "&HpTo=" + HpTo + \
        "&page=" + page

    # connect to bilbasen.dk, download brands and do a GET request for the URI
    conn = connect()
    create_car_brand_table(conn)
    conn.request("GET", query)
    res = conn.getresponse()

    # read the HTML and parse it with BeautifulSoup
    content = res.read()
    parsed_html = BeautifulSoup(content, from_encoding='utf8')

    # create the table in the database
    try:
        cur, con = database.connect_to_database()
        with con:
            date = get_date()
            tablename = 'AllCars' + date
            if database.check_if_table_exist(cur, tablename):
                database.delete_table(cur, tablename)
            command = "CREATE TABLE " + tablename + "(Model CHAR(100), " + \
                "Link CHAR(100), Description MEDIUMTEXT, Kms INT(20), " + \
                "Year INT(4), Kml FLOAT(50), Kmt FLOAT(50), " + \
                "Moth CHAR(30), Trailer CHAR(30), Location CHAR(50), " + \
                "Price INT(20))"
            cur.execute(command)

            # extract total number of pages to crawl
            npages = None
            uls = parsed_html.find('ul', {'class': 'pagination pull-right'})
            count = 0
            lis = uls.find_all('li')
            for li in lis:
                if li.text == '...':
                    npagesstring = lis[count+1].text
                    npages = int(npagesstring.replace('.', ''))
                count += 1

            if limit is None:
                limit = npages
            else:
                limit = int(limit)
            print "pages to crawl: %s" % limit

            # loop through the pages
            while int(page) <= limit:
                print "crawling page " + page

                # extract all cars of the different listing types
                rllplus = parsed_html.find_all(
                    'div', attrs={'class': 'row listing listing-plus'})
                rllexclusive = parsed_html.find_all(
                    'div', attrs={'class': 'row listing listing-exclusive'})
                rlldiscount = parsed_html.find_all(
                    'div', attrs={'class': 'row listing listing-discount'})

                # extract the data and insert the row in the database table
                for listing in rllplus:
                    car = extract_car_info('plus', listing)
                    insert_car_to_table(car, tablename, cur)

                for listing in rllexclusive:
                    car = extract_car_info('exclusive', listing)
                    insert_car_to_table(car, tablename, cur)

                for listing in rlldiscount:
                    car = extract_car_info('discount', listing)
                    insert_car_to_table(car, tablename, cur)

                # go to next page
                incr = int(page)
                incr += 1
                page = str(incr)

                query = "/brugt/bil" + Brand + Model + "?Fuel=" + Fuel + \
                    "&KmlFrom=" + Kmlfrom + "&YearFrom=" + Fromyear + \
                    "&PriceFrom=" + Pricefrom + "&PriceTo=" + Priceto + \
                    "&MileageTo=" + Mileageto + "&ZipCode=" + Zipcode + \
                    "&IncludeEngrosCVR=" + IncludeEngrosCVR + \
                    "&IncludeSellForCustomer=" + IncludeSellForCustomer + \
                    "&IncludeWithoutVehicleRegistrationTax=" + \
                    IncludeWithoutVehicleRegistrationTax + \
                    "&IncludeLeasing=" + IncludeLeasing + "&HpFrom=" + \
                    HpFrom + "&HpTo=" + HpTo + "&page=" + page

                conn.request("GET", query)
                res = conn.getresponse()
                content = res.read()
                parsed_html = BeautifulSoup(content, from_encoding='utf8')

    # in case of database error
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)

    # close connection to database
    if con:
        database.commit(cur, con)


def main():
    """ The method is the main method of the script.

    The which will run by a command 'python bilbasen.py arg',
    where arg is the number of pages to crawl. Do not provide any
    argument if all pages should be crawled.
    """
    if len(sys.argv) == 1:
        download_data_to_database()
    else:
        download_data_to_database(sys.argv[1])

if __name__ == '__main__':
    main()
