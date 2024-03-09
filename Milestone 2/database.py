import mysql.connector
from constants import Constants
import json
import math


class Database:
    def __init__(self):
        # defaults - localhost:3306
        self.db = mysql.connector.connect(
            user=Constants.USER,
            password=Constants.PASSWORD
        )
        self.cursor = self.db.cursor()

    def create_database(self):
        self.cursor.execute("DROP DATABASE IF EXISTS inverted_index")
        self.cursor.execute("CREATE DATABASE inverted_index")
        self.cursor.execute("USE inverted_index")
        self.create_table()
        self.insert_urls()

    def create_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS postings")
        self.cursor.execute("DROP TABLE IF EXISTS documents")
        self.cursor.execute("DROP TABLE IF EXISTS idf")

        self.cursor.execute("CREATE TABLE documents (" +
                            "document_name VARCHAR(10) PRIMARY KEY,"
                            "url VARCHAR(2310))")

        self.cursor.execute("CREATE TABLE postings(" +
                            "term_id INT," +
                            "document_name VARCHAR(10)," +
                            "frequency INT," +
                            "tf FLOAT," +
                            "tag_weight INT," +
                            "PRIMARY KEY(term_id, document_name)," +
                            "FOREIGN KEY(document_name) REFERENCES documents(document_name))")

        self.cursor.execute("CREATE TABLE idf(term_id INT,idf FLOAT)")

    def insert_urls(self):
        # Load bookkeeping.json to create url tables in database
        with open("WEBPAGES_RAW\\bookkeeping.json") as file:
            insert_query = f"INSERT INTO documents (document_name, url) VALUES (%s,%s)"
            data = json.load(file)

            urls = []
            for doc_name, url in data.items():
                urls.append((doc_name, url))

            self.cursor.executemany(insert_query, urls)
            self.db.commit()

    def insert_idf(self, term_totalfreq, total_doc):
        insert_query = f"INSERT INTO idf (term_id,idf) VALUES (%s,%s)"

        # N = total document == total_doc
        # term_totalfreq has document frequency for each term
        # Calculate idf for each term_id
        termID_IDF = []
        for term_id, df in term_totalfreq.items():
            idf = round(math.log(total_doc/df), 4)
            termID_IDF.append((term_id, idf))

        self.cursor.executemany(insert_query, termID_IDF)
        self.db.commit()

    def insert_postings(self, posting):
        insert_query = f"INSERT INTO postings (term_id,document_name,frequency,tf,tag_weight) VALUES (%s,%s,%s,%s,%s)"

        # Insert postings data into database and clears postings list in main memory
        posted = []
        for _, post in posting.values():
            posted.extend(post)
            post.clear()

        self.cursor.executemany(insert_query, posted)
        self.db.commit()

    def merge_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS index_data")
        self.cursor.execute("CREATE TABLE index_data AS " +
                            "SELECT postings.term_id, document_name, frequency, tf, idf, round((tf*idf),4) as tf_idf, " +
                            "tag_weight, round(((tf*idf)+(tag_weight/5)),4) as weight " +
                            "FROM postings join idf " +
                            "ON postings.term_id=IDF.term_id")

    def build_magnitudes(self):
        self.cursor.execute("SELECT document_name, SQRT(SUM(weight * weight)) AS mag " +
                            "FROM index_data " +
                            "GROUP BY document_name")

        # Results as [(doc_name, mag), ...]
        results = self.cursor.fetchall()

        # Convert result into dict
        magnitudes = dict()
        for result in results:
            magnitudes[result[0]] = result[1]
        return magnitudes
