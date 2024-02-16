import mysql.connector
from constants import Constants
from datetime import datetime


class Queries:
    def __init__(self):
        # defaults - localhost:3306
        self.db = mysql.connector.connect(
            user=Constants.USER,
            password=Constants.PASSWORD,
            database=Constants.DATABASE
        )
        self.cursor = self.db.cursor()

    def insert_postings(self, posting):
        insert_query = f"INSERT INTO postings (term_id,document_name,frequency) VALUES (%s,%s,%s)"
        posted = []
        for _, post in posting.values():
            posted.extend(post)
            post.clear()

        self.cursor.executemany(insert_query, posted)
        self.db.commit()


    def query(self, term_id, term):
        self.cursor.execute("select count(url) from postings NATURAL JOIN documents where term_id = %s", (term_id,))
        result = self.cursor.fetchone()
        with open("query.txt", 'a', encoding='utf-8') as f:
            f.write(term + "\n")
            f.write(str(result) + " urls\n")
        self.cursor.execute("select url from postings NATURAL JOIN documents where term_id = %s limit 20", (term_id,))
        result = self.cursor.fetchall()
        with open("query.txt", 'a', encoding='utf-8') as f:
            for row in result:
                f.write(row[0] + "\n")
        print("retrieved: " + term + "\n")



