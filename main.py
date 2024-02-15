from html_content import Indexer
import sys
from queries import Queries


if __name__ == "__main__":
    query = Queries()

    indexer = Indexer(sys.argv[1], query)
    indexer.get_html_content()




