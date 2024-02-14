from html_content import content
import sys
from queries import Queries

if __name__ == "__main__":
    query = Queries()
    Content = content(sys.argv[1],query)
    Content.get_html_content()
    word_list = ["informatics","mondego","irvine"]
    for word in word_list:
        Content.query(word)




