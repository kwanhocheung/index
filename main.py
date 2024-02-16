from html_content import Indexer
import sys
from queries import Queries


if __name__ == "__main__":
    queries = Queries()
    indexer = Indexer(sys.argv[1],queries)
    indexer.get_html_content()
    word_list = ["informatics","mondego","irvine"]
    for word in word_list:
        indexer.query(word)




