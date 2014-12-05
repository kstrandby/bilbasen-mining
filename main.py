# -*- coding: utf-8 -*-
"""
Main script to run the cherrypy web application.

This is the main script of the module and is used to run the cherrypy
web application - run the web application by 'python main.py'
- the web application will run on 127.0.0.1 port 8888

It uses jinja2 to generate HTML from templates specified in the templates
folder.
It consist of a class MiningBilbasen, which contains methods for each site
of the web application (specifying their URLs).
Each method returns the HTML of the site, which is used by cherrypy
to present the site.
"""
import cherrypy
import os
import sys
from jinja2 import Environment, PackageLoader

import datamining
import database
import html
import graphics
import bilbasen

env = Environment(loader=PackageLoader('main', 'templates'))
newest_table = database.get_newest_table()


class MiningBilbasen:

    """ The class contains method used to generate the webpages."""

    def index(self):
        """ The method generates the index page of the web application.

        The page is generated using the jinja2 template
        'index.html' to present it.
        """
        expensivecars = datamining.get_most_expensive_cars(
            newest_table)
        cheapestcars = datamining.get_cheapest_cars(
            newest_table)
        fastestcars = datamining.get_fastest_cars(
            newest_table)
        mostecofriendlycars = datamining.get_most_ecofriendly_cars(
            newest_table)

        expensive = html.create_car_representation(
            expensivecars, 'price')
        cheap = html.create_car_representation(
            cheapestcars, 'price')
        fast = html.create_car_representation(
            fastestcars, 'kmt')
        ecofriendly = html.create_car_representation(
            mostecofriendlycars, 'kml')

        template = env.get_template('index.html')
        html_content = template.render(
            expensive_car=expensive, cheapest_car=cheap,
            fastest_car=fast, ecofriendly_car=ecofriendly)
        return html_content
    index.exposed = True

    def distributions(self):
        """ The method generates the distributions page.

        The page is generated using the jinja2 template
        'distribution_template.html'.
        """
        table = datamining.get_distribution_all_brands(newest_table)
        html_table = html.create_HTMLtable_from_series(
            table, ['car', 'number', 'percentage'])

        graphics.create_distribution_plot(
            table, 20, 'img/brand_distribution.png')
        template = env.get_template('distribution_template.html')
        html_content = template.render(
            title='Distribution of all car brands', htmltable=html_table)
        return html_content
    distributions.exposed = True

    def distribution_of_car_brand(self, brand):
        """ The method generates the distributions_of_car_brand page.

        The page is generated using the jinja2 template
        'distribution_template.html'.
        """
        template = env.get_template('distribution_template.html')
        if database.car_exists(brand):
            table = datamining.get_distribution_one_brand(newest_table, str(brand))
            html_table = html.create_HTMLtable_from_series(
                table, ['car', 'number', 'percentage'])

            graphics.create_distribution_plot(
                table, 20, 'img/brand_distribution.png')
            
            title = 'Distribution of ' + brand + ' models'
            html_content = template.render(
                title=title, htmltable=html_table)
            return html_content
        else:
            return 'Error - car brand ' + brand + ' does not exist'

    distribution_of_car_brand.exposed = True

    def location_distributions(self, brand="all brands"):
        """ The method generates the location_distributions page.

        The page is generated using the jinja2 template
        'location_distribution_template.html'.
        """
        distribution_all_brands = datamining. \
            get_location_distribution_all_brands(newest_table)

        if brand == 'all brands':
            graphics.create_pie_plot(
                distribution_all_brands, 'img/location_distribution.png')
            graphics.create_distribution_map(distribution_all_brands)
        elif database.car_exists(brand):
            distribution = datamining.get_location_distribution_one_brand(
                newest_table, brand)
            graphics.create_pie_plot(
                distribution, 'img/location_distribution.png')
            graphics.create_distribution_map(distribution)
        else:
            return 'Error - car brand ' + brand + ' does not exist'
        template = env.get_template('location_distribution_template.html')
        html_content = template.render(brand=brand)
        return html_content
    location_distributions.exposed = True

    def price_km_year_coherence(self, brand="all brands"):
        """ The method generates the price_km_year_coherence page.

        The page is generated using the jinja2 template
        'price_km_year_coherence_template.html' to
        """
        graphics.create_price_km_scatter(newest_table, brand)
        graphics.create_price_year_scatter(newest_table, brand)
        template = env.get_template('price_km_year_coherence_template.html')
        html_content = template.render(brand=brand)
        return html_content
    price_km_year_coherence.exposed = True

    def best_offer(self, model=None):
        """ The method generates the best_offer page.

        The page is generated using the jinja2 template
        'best_offer_template.html'.
        """
        template = env.get_template('best_offer_template.html')
        show = 'False'
        if not model is None:
            best_offer, saving = datamining.calculate_best_offer(
                newest_table, model)
            if best_offer.empty:
                return 'Error! Car model ' + model + ' does not exist'
            show = 'True'
            pic_src = bilbasen.get_car_image_src(best_offer.Link)
            html_content = template.render(
                best_offer=best_offer, show=show, model_search=model,
                model=best_offer.Model, price=best_offer.Price,
                predicted_price=int(best_offer.Price-saving),
                saving=int(saving), description=best_offer.Description,
                year=best_offer.Year, kms=best_offer.Kms,
                location=best_offer.Location,
                link=('http://www.bilbasen.dk' + best_offer.Link), pic=pic_src)

        else:
            best_offer = ''
            show = False
            html_content = template.render(
                best_offer=None, show=show, model_search=None,
                model=None, price=None, predicted_price=None,
                saving=None, description=None, year=None,
                kms=None, location=None, link=None, pic=None)

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
