import mysql.connector
from constants import Constants
from datetime import datetime


class Queries:
    def __init__(self):
        # defaults - localhost:3306
        self.db = mysql.connector.connect(
            user=Constants.USER,
            password=Constants.PASSWORD
        )
        self.cursor = self.db.cursor()

    def create_postings(self):
        self.cursor.execute("DROP DATABASE IF EXISTS inverted_index")
        self.cursor.execute("CREATE DATABASE inverted_index")
        self.cursor.execute("USE inverted_index")
        self.cursor.execute("CREATE TABLE postings (" +
                            "term_id INT NOT NULL," +
                            "document_name VARCHAR(10) NOT NULL," +
                            "frequency INT NOT NULL," +
                            "PRIMARY KEY (term_id, document_name))")

    def insert_postings(self, posting):
        insert_query = f"INSERT INTO postings (term_id,document_name,frequency) VALUES (%s,%s,%s)"
        posted = []
        for _, post in posting.values():
            posted.extend(post)
            post.clear()

        self.cursor.executemany(insert_query, posted)
        self.db.commit()

        #now = datetime.now()
        #time = now.strftime("%H:%M:%S")
        #print(time + " - Inserted: " + str(posting))
