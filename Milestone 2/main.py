from indexer import Indexer
from searcher import Searcher
from queries import Queries
from database import Database
import sys
import json
from gui_interface import search_gui
from PySide6.QtWidgets import QApplication


if __name__ == "__main__":
    #### UNCOMMENT TO RUN INDEXER BEFORE SEARCH
    #db = Database()
    #indexer = Indexer(sys.argv[1], db)
    #indexer.get_html_content()

    # Import json file contain dictionary of term: term_id
    data = dict()
    with open("term_termId.json") as file:
        data = json.load(file)

    # Import json file with dictionary of doc: magnitudes
    magnitudes = dict()
    with open("magnitudes.json") as file:
        magnitudes = json.load(file)

    query = Queries()
    searcher = Searcher(data, query, magnitudes)
    #searcher.start_search()

    app = QApplication(sys.argv)
    interface = search_gui(sys.argv[1], searcher)
    interface.show()
    sys.exit(app.exec())
