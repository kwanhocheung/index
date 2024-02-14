import mysql.connector
from constants import Constants
import json
class Queries:
    def __init__(self):
        self.db = mysql.connector.connect(
            user=Constants.USER,
            password=Constants.PASSWORD,
            database=Constants.DATABASE,
        )
        self.cursor = self.db.cursor()
    def insert_tuple_of_lists(self, tuple):
        insert_query = f"INSERT INTO tokens (term_id,document_name,frequency) VALUES (%s,%s,%s)"
        self.cursor.execute(insert_query, tuple)
        self.db.commit()
        print("inserted\n")
