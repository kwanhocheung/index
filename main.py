from html_content import Indexer
import sys
from queries import Queries


if __name__ == "__main__":
    queries = Queries()
    indexer = Indexer(sys.argv[1],queries)
    indexer.get_html_content()

    term = "artificial intelligence computer science"
    tokenized_term = indexer.alnum_tokenizer.tokenize(term)
    indexer.get_cosine_similarity(tokenized_term)



