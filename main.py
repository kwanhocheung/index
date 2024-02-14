from html_content import content
import sys
from queries import Queries

if __name__ == "__main__":
    query = Queries()
    Content = content(sys.argv[1],query)
    Content.get_html_content()




