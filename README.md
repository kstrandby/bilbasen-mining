bilbasen-mining
===============
This project was developed as part of the DTU course 02819 Data Mining using Python.
The purpose of the project is to perform data mining of the danish online car shopping site, www.bilbasen.dk. The available data contains information about all the cars currently on sale, such as price, age, mileage done, location of sale, etc. This data is crawled once by the script bilbasen.py and stored more convenient in a local MySQLdb database. The data is used to conduct different statistics, such as the distribution of car brands on sale, distrution of car brands based on the sales location, but also simple statistics to answer questions like "which car is the cheapest?" and "which car is the most expensive?". Data mining techniques are used to evaluate the textual descriptions of the cars and based on that together with other attributes of the cars (mileage, price), a linear regression 
model is calculated and used to predict prices of car models, in order to calculate a
best offer for a certain model.
A cherrypy web application was also developed in order to provide a more graphical view of the findings in the project.

The project consist of the following modules:

bilbasen.py contains only code to download data from bilbasen.dk to a local database. 
  Downloading only needs to be done once. Run script with 'python bilbasen.py <n_pages>', where n_pages is the number of pages to crawl. This argument is optional, and if not 
  provided, all pages will be crawled (usually around 1300 pages with 32 cars on each).

database.py contains convenient methods for communication with the database.

graphics.py contains methods to create different plots to visualize data and results
  from the data mining functions.

html.py contains convenient methods to generate html representations of different data.

tests.py contains unittests of the modules.

datamining.py contains all the data mining functions.

main.py is the main python file, run this to start the webapp on http://localhost:8888


--------------------------------------------------------------------------------------
Running the web application:

1: 	Install MySQL and the MySQLdb module:
   	Linux: 	sudo apt-get install mysql-server
			sudo apt-get install python-mysqldb

2: 	Create a database user and a database to be used for the application:
	mysql>	CREATE DATABASE bilbasendb;
	mysql>  CREATE USER 'user'@'localhost' IDENTIFIED BY 'bilbasen';
	mysql>  USE bilbasendb;
	mysql>  GRANT ALL ON bilbasendb.* TO 'user'@'localhost';
	mysql> quit;

3:  Run the bilbasen.py script to get some data into the database:
	python bilbasen.py
	- if you are in a hurry, specify the number of pages:
	python bilbasen.py <n_pages>

4:  Run the cherrypy application:
	python main.py

5:	Open your browser on localhost:8888 and play around! :)