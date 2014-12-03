# -*- coding: utf-8 -*-
from __future__ import division
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt


def create_distribution_map(distribution):
    # define longitudes and latitudes for the different regions
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

        # for all (except if index is None), append value to the values list
        if index != 'None':
            percentage = (value / value_sum) * 100
            values.append(percentage * 100)
            print index

    m = Basemap(width=490000, height=400000, resolution='i', projection='lcc',
                lat_0=56, lon_0=11.5)
    m.drawcoastlines()
    m.drawmapboundary(fill_color='lightblue')
    m.fillcontinents(color='lightgreen', lake_color='lightblue')

    x, y = m(lons, lats)

    print len(x)
    print len(y)
    print len(values)

    m.scatter(x, y, zorder=3, s=values, c=values, alpha=0.8,
              cmap=plt.cm.cool)

    plt.savefig('img/distributionmap.png', transparent=True)
    plt.clf()
