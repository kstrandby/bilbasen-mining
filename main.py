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
from jinja2 import Environment, PackageLoader

import datamining
import database
import html
import graphics

env = Environment(loader=PackageLoader('main', 'templates'))


index_cache = ""
distribution_cache = ""
location_distribution_cache = ""
price_km_distribution_cache = ""
best_offer_cache = ""

newest_table = database.get_newest_table()


def generate_index_page():
    if not len(index_cache) == 0:
        return index_cache

    expensivecars = datamining.get_most_expensive_cars(newest_table)
    cheapestcars = datamining.get_cheapest_cars(newest_table)
    fastestcars = datamining.get_fastest_cars(newest_table)
    mostecofriendlycars = datamining.get_most_ecofriendly_cars(newest_table)

    expensive = html.create_car_representation(expensivecars, 'price')
    cheap = html.create_car_representation(cheapestcars, 'price')
    fast = html.create_car_representation(fastestcars, 'kmt')
    ecofriendly = html.create_car_representation(mostecofriendlycars, 'kml')

    template = env.get_template('index.html')
    global index_cache
    index_cache = template.render(
        expensive_car=expensive, cheapest_car=cheap,
        fastest_car=fast, ecofriendly_car=ecofriendly)
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

        graphics.create_distribution_plot(table, 20, 'img/brand_distribution.png')
        template = env.get_template('distribution_template.html')
        global distribution_cache
        distribution_cache = template.render(
            title='Distribution of all car brands', htmltable=html_table)
        return distribution_cache
    distributions.exposed = True

    def distribution_of_car_brand(self, brand):
        table = datamining.get_distribution_one_brand(newest_table, str(brand))
        html_table = html.create_HTMLtable_from_series(
            table, ['car', 'number', 'percentage'])

        sliced_table = table[:20]
        sliced_table.plot(kind='barh', x=0)
        plt.tight_layout()
        plt.savefig('img/brand_distribution.png', transparent=True)
        plt.clf()

        template = env.get_template('distribution_template.html')
        title = 'Distribution of ' + brand + ' models'
        html_content = template.render(
            title=title, htmltable=html_table)
        return html_content
    distribution_of_car_brand.exposed = True

    def location_distributions(self, brand="all brands"):
        distribution_all_brands = datamining. \
            get_location_distribution_all_brands(newest_table)

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

        template = env.get_template('location_distribution_template.html')
        html_content = template.render(brand=brand)
        return html_content
    location_distributions.exposed = True

    def price_km_year_coherence(self, brand="all brands"):
        graphics.create_price_km_cluster(newest_table, brand)
        graphics.create_price_year_cluster(newest_table, brand)
        template = env.get_template('price_km_year_coherence_template.html')
        html_content = template.render(brand=brand)
        return html_content
    price_km_year_coherence.exposed = True

    def best_offer(self, model=None):
        template = env.get_template('best_offer_template.html')

        if not model is None:
            car, saving = datamining.calculate_best_offer(newest_table, model)

            best_offer = str(car)
        else:
            best_offer = ''
        html_content = template.render(best_offer=best_offer)
        return html_content
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
