import mysql.connector
from constants import Constants
class queries:
    connection = mysql.connector.connect(user=Constants.USER, password=Constants.PASSWORD, database=Constants.DATABASE)
    cursor = connection.cursor()