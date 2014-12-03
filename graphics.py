# -*- coding: utf-8 -*-
""" Graphics module

    This module contains methods to create plots of different types
    to visualize the data and results from the data mining methods.

"""
from __future__ import division
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from scipy import stats
import pandas
import database


def create_distribution_map(distribution):
    """ Given a distribution as a pandas Series with indexes as locations
        and values as the number of cars at that location, this method
        creates a map of Denmark using Basemap, and plots a scatter plot
        on top of the map. Each scatter will correspond to a location, and
        its size will correspond to the number of cars at that location. """

    """ define longitudes and latitudes for the different regions """
    nordsjaelland_lat = 55.893253
    nordsjaelland_lon = 12.332886
    sydvestsjaelland_lat = 55.300459
    sydvestsjaelland_lon = 11.574829
    fyn_lat = 55.394162
    fyn_lon = 10.377320
    soenderjylland_lat = 55.287949
    soenderjylland_lon = 9.168823
    oestjylland_lat = 56.455885
    oestjylland_lon = 10.064209
    midtvestjylland_lat = 56.141949
    midtvestjylland_lon = 8.657959
    nordjylland_lat = 57.275015
    nordjylland_lon = 9.999294
    lollandfalster_lat = 54.806459
    lollandfalster_lon = 11.717652
    bornholm_lat = 55.124954
    bornholm_lon = 14.931152

    lons = []
    lats = []
    values = []

    value_sum = sum(distribution.values)

    """ loop through the locations and add their latitudes, longitudes and
        values to separate arrays"""

    for index, value in distribution.iteritems():
        print index, value

        if "nordsjælland" in index.decode('utf-8').lower().encode('utf-8'):
            lons.append(nordsjaelland_lon)
            lats.append(nordsjaelland_lat)
        elif "vestsjælland" in index.decode('utf-8').lower().encode('utf-8'):
            lons.append(sydvestsjaelland_lon)
            lats.append(sydvestsjaelland_lat)
        elif "fyn" in index.decode('utf-8').lower().encode('utf-8'):
            lons.append(fyn_lon)
            lats.append(fyn_lat)
        elif "sønderjylland" in index.decode('utf-8').lower().encode("utf-8"):
            lons.append(soenderjylland_lon)
            lats.append(soenderjylland_lat)
        elif "østjylland" in index.decode('utf-8').lower().encode('utf-8'):
            lons.append(oestjylland_lon)
            lats.append(oestjylland_lat)
        elif "vestjylland" in index.decode('utf-8').lower().encode('utf-8'):
            lons.append(midtvestjylland_lon)
            lats.append(midtvestjylland_lat)
        elif "nordjylland" in index.decode('utf-8').lower().encode('utf-8'):
            lons.append(nordjylland_lon)
            lats.append(nordjylland_lat)
        elif "lolland" in index.decode('utf-8').lower().encode('utf-8'):
            lons.append(lollandfalster_lon)
            lats.append(lollandfalster_lat)
        elif "bornholm" in index.decode('utf-8').lower().encode('utf-8'):
            lons.append(bornholm_lon)
            lats.append(bornholm_lat)

        """ for all (except if index is None), append value to the values list """
        if index != 'None':
            percentage = (value / value_sum) * 100
            values.append(percentage * 100)
            print index

    """ create the map of Denmark """
    m = Basemap(width=490000, height=400000, resolution='i', projection='lcc',
                lat_0=56, lon_0=11.5)
    m.drawcoastlines()
    m.drawmapboundary(fill_color='lightblue')
    m.fillcontinents(color='lightgreen', lake_color='lightblue')

    """ plot the values and save the plot """
    x, y = m(lons, lats)
    m.scatter(x, y, zorder=3, s=values, c=values, alpha=0.8,
              cmap=plt.cm.cool)

    plt.savefig('img/distributionmap.png', transparent=True)
    plt.clf()


def create_price_km_scatter(table, brand):
    """ This method creates a scatter plot showing the coherence 
        between prices and mileage (in km's). """

    cur, con = database.connect_to_database()
    query = ''
    if brand == 'all brands':
        query = 'SELECT * FROM ' + table
    else:
        query = "SELECT * FROM " + table + \
            " WHERE Model LIKE '%%%" + brand + "%%%'"
    result = pandas.read_sql_query(query, con)
    y = result.Price
    x = result.Kms

    """ define default x- and y-ranges to cut off outliers for
        plots of all brands """
    default_xmin = 0
    default_xmax = 600000
    default_ymin = 0
    default_ymax = 2500000

    """ for specific brands, use the minimum and maximum values """
    if brand != 'all brands':
        default_xmin = min(x.values)
        default_xmax = max(x.values)
        default_ymin = min(y.values)
        default_ymax = max(y.values)

    plt.plot(x, y, 'o')
    plt.xlim(default_xmin, default_xmax)
    plt.ylim(default_ymin, default_ymax)
    plt.xlabel('Kilometers')
    plt.ylabel('Price')
    plt.tight_layout()
    plt.savefig('img/price_km_scatter', transparent=True)
    plt.clf()


def create_price_year_scatter(table, brand):
    """ This method creates a scatter plot showing the coherence 
        between prices and age (in production year). """

    cur, con = database.connect_to_database()
    query = ''
    if brand == 'all brands':
        query = 'SELECT * FROM ' + table
    else:
        query = "SELECT * FROM " + table + \
            " WHERE Model LIKE '%%%" + brand + "%%%'"
    result = pandas.read_sql_query(query, con)
    y = result.Price
    x = result.Year

    """ define default x- and y-ranges to cut off outliers for
        plots of all brands """
    default_xmin = 1950
    default_xmax = 2016
    default_ymin = 0
    default_ymax = 2500000

    """ for specific brands, use the minimum and maximum values """
    if brand != 'all brands':
        default_xmin = min(x.values)
        default_xmax = max(x.values)
        default_ymin = min(y.values)
        default_ymax = max(y.values)

    plt.plot(x, y, 'o')
    plt.xlim(default_xmin, default_xmax)
    plt.ylim(default_ymin, default_ymax)
    plt.xlabel('Year')
    plt.ylabel('Price')
    plt.tight_layout()
    plt.savefig('img/price_year_scatter', transparent=True)
    plt.clf()


def create_distribution_plot(table, n_bars, plot_name):
    """ This method creates a bar plot showing the distribution of the
        data in the table, which has to be a pandas DataFrame.
        The plot will only include the specified number of bars (n_bars),
        as otherwise it can become very crowded. """
    sliced_table = table[:n_bars]
    sliced_table.plot(kind='barh', x=0)
    plt.tight_layout()
    plt.savefig(plot_name, transparent=True)
    plt.clf()