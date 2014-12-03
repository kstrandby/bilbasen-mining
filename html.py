# -*- coding: utf-8 -*-
from django.utils.encoding import smart_str
from bs4 import BeautifulSoup
import bilbasen


def create_HTMLtable_from_series(series, listofheaders):
    htmltable = '<table><tr>'
    for header in listofheaders:
        htmltable += '<th>' + header + '</th>'
    htmltable += '</tr>'

    for index, row in series.iterrows():
        htmltable += '<tr>'
        for column in row:
            if type(column) == str:
                column = smart_str(column)
            htmltable += '<td>' + smart_str(column) + '</td>'
        htmltable += '</tr>'
    htmltable += '</table>'
    return htmltable


def create_car_representation(cars, attribute):
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
        print rep

        # download a picture of the car from bilbasen.dk
        conn = bilbasen.connect()
        conn.request("GET",  car.Link)
        res = conn.getresponse()
        content = res.read()
        parsed_html = BeautifulSoup(content, from_encoding='utf8')
        pics = parsed_html.find_all('a', {'id': 'bbVipGalleryLarge0'})
        rep += """<div id="carpics">"""
        for pic in pics:
            src = pic.find('img')['data-src']
            rep += """<img src=" """ + src + """ ">"""
        rep += "</div>"
        return rep
    return rep
