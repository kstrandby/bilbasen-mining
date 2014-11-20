bilbasen-mining
===============
bilbasen.py contains only code to download data from bilbasen.dk to a local database. 
  Downloading only needs to be done once.

database.py contains convenient methods for communication with the database.

graphics.py currently contains a single method used to generate a distribution map using Basemap.

html.py contains convenient methods to generate html representations of different data.

tests.py contains unittests of the modules.

datamining.py contains all the data mining. It should be noted, that the method calculateBestOffer() is 
  currently not used by the cherrypy webapplication.

main.py is the main python file, run this to start the webapp on http://localhost:8888

