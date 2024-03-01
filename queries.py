import mysql.connector
from constants import Constants
from datetime import datetime
import math


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
        insert_query = f"INSERT INTO postings (term_id,document_name,frequency,tf) VALUES (%s,%s,%s,%s)"
        posted = []
        for _, post in posting.values():
            posted.extend(post)
            post.clear()

        self.cursor.executemany(insert_query, posted)
        self.db.commit()
    def insert_idf(self,term_totalfreq,total_doc):
        insert_query = f"INSERT INTO idf (term_id,idf) VALUES (%s,%s)"
        termID_IDF = []
        for x, y in term_totalfreq.items():
            idf = round(math.log(total_doc/y), 4)
            termID_IDF.append((y, idf))

        self.cursor.executemany(insert_query, termID_IDF)
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



