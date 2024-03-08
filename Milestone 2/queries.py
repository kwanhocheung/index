import mysql.connector
from constants import Constants


class Queries:
    def __init__(self):
        # defaults - localhost:3306
        self.db = mysql.connector.connect(
            user=Constants.USER,
            password=Constants.PASSWORD,
            database=Constants.DATABASE
        )
        self.cursor = self.db.cursor()

    def get_index(self, term_id):
        self.cursor.execute("SELECT index_data.document_name, weight, url " +
                            "FROM index_data join documents on index_data.document_name = documents.document_name " +
                            "WHERE term_id = %s",(term_id,))

        # Result will be [(doc_name, weight, url), ...]
        result = self.cursor.fetchall()
        return result

    def get_doc_vector(self, term_id):
        self.cursor.execute("SELECT term_id, document_name, weight FROM index_data WHERE term_id = %s", (term_id,))

        # Result will be [(term_id, doc_name, weight), ...]
        result = self.cursor.fetchall()
        return result

    def get_query_vector(self, term_id):
        self.cursor.execute("SELECT term_id, idf FROM idf WHERE term_id = %s", (term_id,))
        result = self.cursor.fetchall()
        return result
