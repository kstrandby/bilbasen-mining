bilbasen-mining
===============
This project was developed as part of the DTU course 02819 Data Mining using Python.
The purpose of the project is to perform data mining of the danish online car shopping site, www.bilbasen.dk. The available data contains information about all the cars currently on sale, such as price, age, mileage done, location of sale, etc. This data is crawled once by the script bilbasen.py and stored more convenient in a local MySQLdb database. The data is used to conduct different statistics, such as the distribution of car brands on sale, distrution of car brands based on the sales location, but also simple statistics to answer questions like "which car is the cheapest?" and "which car is the most expensive?". Data mining techniques are used to evaluate the textual descriptions of the cars and based on that together with other attributes of the cars (mileage, price), a cluster analysis is performed to find the mean car in a specific car population.
A cherrypy web application was also developed in order to provide a more graphical view of the findings in the project.

The project consist of the following modules:

bilbasen.py contains only code to download data from bilbasen.dk to a local database. 
  Downloading only needs to be done once.

database.py contains convenient methods for communication with the database.

graphics.py currently contains a single method used to generate a distribution map using Basemap.

html.py contains convenient methods to generate html representations of different data.

tests.py contains unittests of the modules.

datamining.py contains all the data mining. It should be noted, that the method calculateBestOffer() is 
  currently not used by the cherrypy webapplication.

main.py is the main python file, run this to start the webapp on http://localhost:8888

