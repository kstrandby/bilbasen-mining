# -*- coding: utf-8 -*-
"""
Created on Tue Oct 21 18:07:28 2014

@author: kristine
"""
from django.utils.encoding import smart_str
import cherrypy
import os
import sys
import matplotlib.pyplot as plt

import datamining
import database
import html
import graphics


index_cache = ""
distribution_cache = ""
location_distribution_cache = ""
price_km_distribution_cache = ""
best_offer_cache = ""

header = """<html>
            <head>
                <title>Data Mining of Bilbasen.dk</title>
                <link rel="stylesheet" type="text/css" href="static/style.css">
            </head>
            <body>
            <div id="wrapper">
        """
footer = """</div>
            <div id="footer">
                <hr />
                <p class="legalese">© 2014 Data Mining of Bilbasen.dk </p>
            </div>
            </body>
            </html>
        """
newest_table = database.get_newest_table()


def generate_index_page():
    if not len(index_cache) == 0:
        return index_cache

    expensivecars = datamining.get_most_expensive_cars(newest_table)
    cheapestcars = datamining.get_cheapest_cars(newest_table)
    fastestcars = datamining.get_fastest_cars(newest_table)
    mostecofriendlycars = datamining.get_most_ecofriendly_cars(newest_table)

    body = """<div id="content">
                <div id="menu">
                <h1>Data mining of
                 <a href="http://www.bilbasen.dk">www.bilbasen.dk</a></h1>
                <ol>
                    <li>
                        <h3> <a href="distributions">Distribution of
                         car models</a>
                        </h3>
                    </li>
                    <li>
                    <h3> <a href="location_distributions">Distribution
                    of car models based on locations</a> </h3> </li>
                   <li><h3> <a href="price_km_connection">Connection between KMs and prices</a></h3></li>
                   <li><h3> <a href="best_offer">Find the best offer for a certain car model</a></h3></li>
                   
               </ol>
               </div>
               <div id="datamining">"""

    if len(expensivecars) > 1:
        body += "<h4>Most Expensive Cars: </h4>"
    else:
        body += "<h4>Most Expensive Car: </h4>"

    body += html.create_car_representation(expensivecars, 'price')
    if len(cheapestcars) > 1:
        body += "<h4>Cheapest Cars: </h4>"
    else:
        body += "<h4>Cheapest Car: </h4>"
    body += html.create_car_representation(cheapestcars, 'price')
    if len(fastestcars) > 1:
        body += "<h4>Fastest Cars: </h4>"
    else:
        body += "<h4>Fastest Car: </h4>"
    body += html.create_car_representation(fastestcars, 'kmt')

    if len(mostecofriendlycars) > 1:
        body += "<h4>Most Ecofriendly Cars: </h4>"
    else:
        body += "<h4>Most Ecofriendly Car: </h4>"
    body += html.create_car_representation(mostecofriendlycars, 'kml')
    body += "</div></div>"

    global index_cache
    index_cache = header + body + footer
    return index_cache


class MiningBilbasen:
    def index(self):
        page = generate_index_page()
        return page
    index.exposed = True

    def distributions(self):
        if not len(distribution_cache) == 0:
            return distribution_cache
        table = datamining.get_distribution_all_brands(newest_table)
        html_table = html.create_HTMLtable_from_series(
            table, ['car', 'number', 'percentage'])

        table.plot(kind='barh', x=0)

        plt.savefig('img/brand_distribution.png', transparent=True)

        plt.clf()

        body = """
        <div id="content">
                    <h1>Distribution of all car brands</h1>
                    <div id="table">""" + html_table + """</div>
                    <div id="plot"><img src="/img/brand_distribution.png"/>

                    <h1>Distribution of models of a particular car brand</h1>
                    <form action="distribution_of_car_brand" method="post">
                        <table summary=""><tbody><tr>
                        <th><label for="carbrand">Car brand:</label></th>
                        <td><input type="text" name="brand"/></td>
                        </tr><tr>
                        <td></td>
                        <td>
                            <input type="submit" value="Show distribution" />
                        </td></tr>
                        </tr></tbody></table>
                    </form>
                </div>
                </div>
                """

        global distribution_cache
        distribution_cache = header + body + footer
        return distribution_cache
    distributions.exposed = True

    def distribution_of_car_brand(self, brand):
        table = datamining.get_distribution_one_brand(newest_table, str(brand))
        body = html.create_HTMLtable_from_series(
            table, ['car', 'number', 'percentage'])
        return header + body + footer
    distribution_of_car_brand.exposed = True

    def location_distributions(self, brand="all brands"):
        distribution_all_brands = datamining. \
            get_location_distribution_all_brands(newest_table)

        body = '<h1> Distribution of cars based on sale location </h1><div id="content">'

        if brand == 'all brands':
            # create pie chart of the distribution
            distribution_all_brands.plot(kind='pie')
            plt.savefig('img/location_distribution.png', transparent=True)
            plt.clf()

            # create map
            graphics.create_distribution_map(distribution_all_brands)
        else:

            distribution = datamining.get_location_distribution_one_brand(
                newest_table, brand)

            # create pie chart of the distribution
            distribution.plot(kind='pie')
            plt.savefig('img/location_distribution.png', transparent=True)
            plt.clf()

            # create map
            graphics.create_distribution_map(distribution)

        body += """<p>The pie chart shows the distribution of """ + smart_str(brand) + """ based on sales locations. <br> To see a pie chart of the distribution of a particular car
        brand, enter the <br> car brand that you want to see below:</p>
        <form action="location_distributions" method="post">
                        <table summary=""><tbody><tr>
                       <th><label for="carbrand">Car brand:</label></th>
                       <td><input type="text" name="brand"/></td>
                        </tr><tr>
                        <td></td>
                        <td>
                            <input type="submit" value="Show distribution" />
                        </td></tr>
                        </tr></tbody></table>
                    </form>
                    <div id=distplot>
                    <img src="img/location_distribution.png"/>
                    <img src="img/distributionmap.png"</div></div>"""

        return header + body + footer
    location_distributions.exposed = True

    def price_km_connection(self):
        body = "Not implemented yet"
        return header + body + footer
    price_km_connection.exposed = True

    def best_offer(self, model=None):
        body = """<h1>Best offer</h1>
                    <div id="content">
                    <p>Enter car model below to get the best offer:</p>
                    <form action="bestoffer" method="post">
                        <table summary=""><tbody><tr>
                        <th><input type="text" name="model"/></td>
                        </tr><tr>
                        <td></td>
                        <td>
                            <input type="submit" value="Get best offer" />
                        </td></tr>
                        </tr></tbody></table>
                    </form>
                    """
        if not model is None:
            datamining.calculate_best_offer(newest_table, model)
            body += "Here will the best offer be shown"
        body += '</div>'
        return header + body + footer
    best_offer.exposed = True

if __name__ == '__main__':
    # set the directory
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    except:
        current_dir = os.path.dirname(
            unicode(sys.executable, sys.getfilesystemencoding()))

    conf = {
        'global': {
            'log.screen': True,
            'server.socket_host': '127.0.0.1',
            'server.socket_port': 8888,
            'engine.autoreload_on': True,
            'log.error_file': os.path.join(current_dir, 'log/errors.log'),
            'log.access_file': os.path.join(current_dir, 'log/access.log'),
        },
        '/': {
            'tools.staticdir.root': current_dir,
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'static',
            'tools.encode.on': False,
            'tools.encode.encoding': 'utf-8',
        },
        '/img': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(current_dir, 'img')}
        }

cherrypy.quickstart(MiningBilbasen(), '/', conf)
