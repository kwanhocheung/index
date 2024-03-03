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
        for term_id, df in term_totalfreq.items():
            idf = round(math.log(total_doc/df), 4)
            termID_IDF.append((term_id, idf))

        self.cursor.executemany(insert_query, termID_IDF)
        self.db.commit()


    def query_geturls(self, term_id):
        self.cursor.execute("select url from postings NATURAL JOIN documents where term_id = %s", (term_id,))
        result = self.cursor.fetchall()
        # convert tuple of list to list
        set_of_urls_result = set(sum(result, ()))
        return set_of_urls_result

    def create_table(self):
        self.cursor.execute("drop table if exists postings")
        self.cursor.execute("drop table if exists idf")
        self.cursor.execute("CREATE TABLE postings(term_id int,document_name varchar(10),frequency int,tf float4,primary key(term_id,document_name),FOREIGN KEY (document_name) references documents(document_name))")
        self.cursor.execute("create table IDF(term_id int,idf float4)")
    def merge_table(self):
        self.cursor.execute("drop table if exists tf_idf")
        self.cursor.execute("create table tf_idf as select postings.term_id, document_name, frequency, tf, idf, round((tf*idf),4) as tf_idf from postings join idf on postings.term_id=IDF.term_id")