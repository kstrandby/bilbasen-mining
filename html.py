# -*- coding: utf-8 -*-
""" html module

    This module contains convenient methods to create html representations
    of various data types.

"""
from django.utils.encoding import smart_str
from bs4 import BeautifulSoup
import bilbasen
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def create_HTMLtable_from_series(series, listofheaders):
    """ This method creates a html table from a Pandas Series, with
        headers as provided in the listofheaders. """
    htmltable = '<table><tr>'
    for header in listofheaders:
        htmltable += '<th>' + header + '</th>'
    htmltable += '</tr>'

    for index, row in series.iterrows():
        htmltable += '<tr>'
        for column in row:
            htmltable += '<td>' + str(column) + '</td>'
        htmltable += '</tr>'
    htmltable += '</table>'
    return htmltable


def create_car_representation(cars, attribute):
    """ This method creates a html div containing specific information,
        which depends on the given attribute. It also downloads a picture
        of the car to represent in the div from bilbasen.dk """
    rep = """<div id="carinf"><p>"""
    for index, car in cars.iterrows():
        rep += smart_str(car.Model)
        if attribute == 'price':
            rep += "</p><p>Price: " + str(car.Price) + "DKK </p></div>"
        elif attribute == 'kmt':
            rep += "</p><p>From 0-100 kmt/t: " + str(car.Kmt) \
                + "secs </p></div>"
        elif attribute == 'kml':
            rep += "</p><p>Kilometers per liter: " + str(car.Kml) \
                + "km/l </p></div>"

        # download a picture of the car from bilbasen.dk
        img_src = bilbasen.get_car_image_src(car.Link)
        rep += '<div id="carpics"><img src="' + img_src + '"></div>'

        return rep

