from html_content import Indexer
import sys
from queries import Queries


if __name__ == "__main__":
    queries = Queries()
    indexer = Indexer(sys.argv[1],queries)
    #indexer.get_html_content()

    term = "artificial intelligence computer science"
    tokenized_term = indexer.alnum_tokenizer.tokenize(term)
    """
    urls_list = indexer.query_get_urls(tokenized_term)
    with open("urls.txt", 'a', encoding='utf-8') as f:
        f.write(term + "\n")
        for row in urls_list:
            f.write(row + "\n")

    index_dict = indexer.query_get_index(tokenized_term)
    with open("index.txt", 'a', encoding='utf-8') as f:
        f.write(term + "\n")
        for doc, total_tf_idf in index_dict.items():
            f.write(doc + ": " + str(total_tf_idf) + "\n")
    """
    indexer.query_get_score(tokenized_term)


