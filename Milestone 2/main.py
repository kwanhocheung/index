from indexer import Indexer
from searcher import Searcher
from queries import Queries
from database import Database
import sys
import json


if __name__ == "__main__":
    #### UNCOMMENT TO RUN INDEXER BEFORE SEARCH
    #db = Database()
    #indexer = Indexer(sys.argv[1], db)
    #indexer.get_html_content()
    #indexer.save_terms()

    # Import json file contain dictionary of
    data = dict()
    with open("term_termId.json") as file:
        data = json.load(file)

    query = Queries()
    searcher = Searcher(data, query)
    searcher.start_search()
