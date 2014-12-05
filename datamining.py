# -*- coding: utf-8 -*-
""" This module contains all the data mining methods. """

from __future__ import division
from decimal import *
from django.utils.encoding import smart_str
import statsmodels.api as sm
import numpy as np
import pandas
import re
import nltk
import itertools
import graphics
import database


def get_distribution_all_brands(tablename):
    """ Calculate a frequency distribution of all car brands.

    The method takes as input the name of a table in the database,
    and returns a panda dataframe of the distribution with brand-names
    in the first column, the number a brand appears in the table in
    the second column and the corresponding percentage in the last
    column.
    """
    cur, con = database.connect_to_database()
    query = "select * from " + tablename
    result = pandas.read_sql_query(query, con)

    # get the model column and the number of models
    models = result.Model
    n_models = len(models)

    models = extract_brands(models)
    columns = ['Brand', 'Number', 'Percentage']
    return create_distribution(models, columns, n_models)


def get_distribution_one_brand(tablename, brand):
    """ Calculate a frequency distribution of a particular car brand.

    The method takes as input the name of a table in the database, and
    a car brand, and calculates a frequency distribution of the models
    for that brand.
    Returns a panda dataframe of the distribution with model-names in
    the first column, the number a model appears in the table in the
    second column, and the corresponding percentage in the last column.
    """
    # get the rows with the specified brand
    cur, con = database.connect_to_database()
    query = "SELECT * FROM " + tablename + \
        " WHERE Model LIKE '%%%" + brand + "%%%'"
    result = pandas.read_sql_query(query, con)

    #get the model column and number of models
    models = result.Model
    n_models = len(models)
    if n_models == 0:  # make sure it isn't empty
        return []

    # dont distinguish models on stuff like 5doors or 4doors, and engine size
    models = simplify_model_names(models)
    columns = ['Model', 'Number', 'Percentage']
    return create_distribution(models, columns, n_models)


def create_distribution(series, columns, n_models):
    """ Calculate a frequency distribution of a Pandas Series.

    The function takes as input a panda series object and calculates
    the frequency distribution.
    Return a panda dataframe object containing the frequency distribution
    with the values of the given series as the first column, the number of
    time a certain value appear in the given series in	the second column,
    and the corresponding percentage in the third column. The DataFrame
    object returned will have labelled columns according to the given
    columns list.
    """
    # create a frequency distribution of the models
    fdist = nltk.FreqDist(series)
    # create a list from the frequency distribution with percentages included
    brand_dist_table = []
    for key in fdist.keys():
        percentage = (Decimal(fdist.get(key)) * Decimal(100)
                      / Decimal(n_models))
        brand_dist_table.append([key, fdist.get(key), '%.2f%%'
                                % round(percentage, 2)])

    # create a pandas dataframe from the list and return it
    dist = pandas.DataFrame.from_records(brand_dist_table, columns=columns)
    return dist


def get_location_distribution_all_brands(table):
    """ Calculate the distribution of all brands based on sale locations.

    The method calculates the distribution of all car brands in the specified
    table. A pandas Series with the distribution and the locations as index
    is returned.
    """
    # get all the different locations present in the specified table
    locations = database.get_locations(table)

    # calculate the distribution
    index_names = []
    distribution = []
    for index, location in locations.iterrows():
        # find all the for each location
        cur, con = database.connect_to_database()
        query = "SELECT * FROM " + table + " WHERE Location LIKE '%%%" \
            + location.location + "%%%';"
        result = pandas.read_sql_query(query, con)

        index_names.append(smart_str(location.location))
        distribution.append(len(result))

    location_distribution = pandas.Series(distribution, index=index_names)
    return location_distribution


def get_location_distribution_one_brand(table, brand):
    """ Calculate the distribution of a car brand based on sale locations.

    The method takes as input the name of a table in the database and a car
    brand. It calculates the distribution based on locations and returns a
    Pandas Series with the distribution and the locations as index.
    """
    # get the rows from the table with the specified brand
    cur, con = database.connect_to_database()

    # get all the different locations present in the specified table
    locations = database.get_locations(table)

    # calculate the distribution
    index_names = []
    distribution = []
    for index, location in locations.iterrows():
        # find all the rows with the specified brand for each location
        query = "SELECT * FROM " + table + " WHERE Model LIKE '%%%" \
            + brand + "%%%' AND Location LIKE '%%%" \
            + location.location + "%%%';"
        result = pandas.read_sql_query(query, con)
        index_names.append(smart_str(location.location))
        distribution.append(len(result))

    location_distribution = pandas.Series(distribution, index=index_names)
    return location_distribution


def extract_brands(models):
    """ Extract brand names from the given list of models.

    The method takes as input a list of models, e.g.
    ["Audi A8", "Mercedes SLK"], and extracts and returns the model names,
    e.g. ["Audi", "Mercedes"] will be extracted and returned.
    """
    all_brands = database.get_car_brands()
    extracted_brands = []
    for car in models:
        #car = smart_str(car)
        for brand in all_brands:
            #	brand = smart_str(brand)
            if brand in car:
                extracted_brands.append(brand)
    return extracted_brands


def simplify_model_names(models):
    """ Simplify car model names in a given list of models.

    The method removes irrelevant information in the names,
    number of doors ('4d'), size of engine ('2.0L') etc.
    before returning the list.
    """
    modified_models = []
    for m in models:
        regex = re.findall(re.compile('\w+(?:-\w+)+|\w+'), m)
        regex = [word for word in regex if not re.search('[0-9]d', word)]
        regex = [word for word in regex if not len(str(word)) < 2]
        regex = [word for word in regex if not re.search(
            r'\b\d+\b', word)]
        modified_models.append(' '.join(regex))
    return modified_models


def get_fastest_cars(table):
    """ Find the fastest car(s) in the given table.

    The method finds the car(s) that goes fastest from 0-100 km/t).
    The result is returned as a pandas DataFrame containing the
    entire database row of that car.
    """
    cur, con = database.connect_to_database()
    query = "SELECT t.* FROM " + table + " t WHERE t.kmt = \
        (select min(subt.kmt) from " + table + " subt where \
        (subt.kmt > 0));"
    return pandas.read_sql_query(query, con)


def get_cheapest_cars(table):
    """ Find the cheapest car(s) in the given table.

    The method finds the cheapest car in the given table, that is
    not 0DKK and is not a leasing car. The result is returned as
    a pandas DataFrame containing the entire database row of that car.
    """
    cur, con = database.connect_to_database()
    query = "SELECT t.* FROM " + table + " t WHERE t.price = \
        (select min(subt.price) from " + table + " subt where \
        (subt.price > 0));"
    return pandas.read_sql_query(query, con)


def get_most_expensive_cars(table):
    """ Find the most expensive car(s) in the given table.

    The result is returned as a pandas DataFrame containing the
    entire database row of that car.
    """
    cur, con = database.connect_to_database()
    query = "SELECT t.* FROM " + table + " t WHERE t.price = \
        (select max(subt.price) from " + table + " subt);"
    return pandas.read_sql_query(query, con)


def get_most_ecofriendly_cars(table):
    """ Find the most eco friendly car(s) in a given table.

    The car(s) that goes most KMs on a liter petrol.
    The result is returned as a pandas DataFrame containing the
    entire database row of that car.
    """
    cur, con = database.connect_to_database()
    query = "SELECT t.* FROM " + table + " t WHERE t.kml = \
        (select max(subt.kml) from " + table + " subt where \
        (subt.kml > 0));"
    return pandas.read_sql_query(query, con)


def analyze_description(description):
    u""" A very simple sentiment analysis function.

    Assigns a score to a sentence, based on how many positive or
    negative words appear in that sentence. If there are no
    negative or positive words,	the final score will be 0. If
    there are more positive than negative words, the score will
    be positive - how positive will depend on how many
    positive / negative words. As it it most likely that there
    will be many positive words compared to negative words, a
    negative word is counted twice, as the score should reflect a
    clear difference between a car description containing only
    positive words, and a car description containing words like
    "buler" and "dårligt", which clearly is a worse car.
    """
    positives = [u'attraktiv', u'nysynet', u'rustfri',
                 u'undervogsbehandlet', u'velholdt', u'nye',
                 u'ny', u'perfekt', u'ok', u'ekstraudstyr',
                 u'parkeringssensor', u'fartpilot', u'kørecomputer',
                 u'startspærre', u'varme', u'regnsensor', u'sædevarme',
                 u'tågelygter', u'airbags', u'airbag', u'abs', u'esp',
                 u'servo', u'el-ruder', u'antispin', u'aut.gear',
                 u'stemmestyring', u'servostyring', u'ratbetjent',
                 u'multifunktionsrat', u'læderrat',
                 u'multifunktionslæderrat', u'komfortblink',
                 u'kopholder', u'dødvinkelsassistent', u'sporassistent',
                 u'klimaanlæg', u'el-betjent', u'el-betjente',
                 u'ortopædisk', u'lygtevasker', u'bakkamera',
                 u'parktronic', u'økonomisk', u'anhængertræk',
                 u'fjernbetjent', u'fjernbetjente', u'fjernbetjening',
                 u'fjernb', u'garanti', u'alufælge', u'alu-fælge',
                 u'topudstyret', u'eljusterbare', u'eljusterbar',
                 u'ventilation', u'fjernlys', u'bluetooth',
                 u'dab', u'højtallersystem',	u'integreret', u'komfort',
                 u'automatik', u'automatisk', u'auto', u'elektrisk',
                 u'elektriske' u'soltag', u'solskærme', u'antiblænd',
                 u'alarm', u'xenonlygter', u'sportslæderrat', u'klimaaut',
                 u'klimaautomatik', u'el-sæder', u'control', u'multirat',
                 u'radio', u'aux-tilslutning', u'auto-hold', u'autohold',
                 u'partikelfilter', u'ekstra', u'usb/audio', u'alarm',
                 u'klima-anlæg', u'fuldautomatisk', u'fuldautomatiske',
                 u'læderarmlæn', u'læder', u'infocenter', u'nedbl',
                 u'sportssæder', u'tonede', u'nyserviceret', u'udstyr',
                 u'finansiering']

    negatives = [u'rustet', u'trænger', u'rust', u'rustarbejde',
                 u'mangler', u'bule', u'buler', u'dårligt', u'dårlige',
                 u'dårlig', u'rustpletter', u'rustplet', u'skadet',
                 u'skade', u'skader', u'defekt', u'defekte', u'falmet',
                 u'falmede', u'hul', u'huller', u'ridse', u'ridser',
                 u'ridsede', u'dele', u'driller']

    words = description.split()
    n_words = len(words)
    positive_count = 0
    negative_count = 0
    for word in words:
        word = word.lower()
        word = word.replace(',', '')
        if word in positives:
            positive_count += 1
        elif word in negatives:
            negative_count += 1
    if n_words != 0:
        return (positive_count - (2*negative_count))/n_words
    else:
        return 0


def calculate_best_offer(table, model):
    """ Calculate the best offer for a given car model.

    The calculation is based on creating a linear regression model
    of the attributes: car description, mileage and age,
    with prices as y-values. The description of the car is analyzed
    to get a rank value, using the modules analyze_description method.
    Based on the linear regression model, a prediction of the prices
    is calculated, and the differences between the predicted prices and
    the actual prices are calculated to find the biggest difference (the
    largest negative value), which is the best offer.
    The returned result is a pandas DataFrame along with the
    difference.
    """
    # get all the offers for the specified model
    keywords = model.split()
    cur, con = database.connect_to_database()
    query = "SELECT * FROM " + table + " WHERE Model LIKE '%%%" \
        + keywords[0] + "%%%'"
    if len(keywords) > 1:
        for keyword in itertools.islice(keywords, 1, len(keywords)):
            query += " AND Model LIKE '%%%" + keyword + "%%%'"

    else:
        query += ";"

    result = pandas.read_sql_query(query, con)
    if len(result) == 0:
        return pandas.Series([]), None

    """ create data array of [description_score, price, kms, year] """
    data = []
    for index, car in result.iterrows():
        if car.Price != 0:  # do not include cars with price = 0
            rank = analyze_description(car.Description)
            data.append([rank, car.Kms, car.Year, car.Price])

    columns = ['rank', 'kms', 'year', 'price']
    dat = pandas.DataFrame.from_records(data, columns=columns)

    # create regression plot
    graphics.create_3D_regression_plot(dat, model)
    """ y (price) will be the response, and X (rank, kms, year)
    will be the predictors """
    X = dat.iloc[:, [0, 1, 2]]
    y = dat.iloc[:, [3]]
    
    """ add a constant term to the predictors to fit the intercept of
    the linear model """
    X = sm.add_constant(X)

    """ calculate the linear regression model with price as y-value
    to get the prediction values """
    reg_model = sm.OLS(y, X).fit()
    predictions = reg_model.predict()

    """ create a numpy array of the differences between the predicted values
    and the actual values for the prices and find the minimum - this is
    the best offer """
    differences = y.price.values - predictions
    smallest = np.amin(differences, axis=0)
    index = differences.argmin(axis=0)
    best_offer = result.loc[index]

    return best_offer, smallest
