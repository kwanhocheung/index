from html_content import Indexer
import sys
from queries import Queries


if __name__ == "__main__":
    queries = Queries()
    indexer = Indexer(sys.argv[1],queries)
    #indexer.get_html_content()

    term = "artificial intelligence computer science"
    tokenized_term = indexer.alnum_tokenizer.tokenize(term)

    index_dict = indexer.query_get_index(tokenized_term)
    cos_list = indexer.get_low_cos(tokenized_term)
    # the set store the doc which are no similar
    new_set = set()
    for key, value in cos_list:
        x = key.split(",")
        new_set.add(x[0])
        new_set.add(x[1])
    for k in list(index_dict.keys()):
        if k not in new_set:
            del index_dict[k]
    with open("result.txt", 'a', encoding='utf-8') as f:
        f.write(term + "\n")
        for doc, data in index_dict.items():
            f.write(doc + ": " + str(data[0]) + " " + data[1] + "\n")


    #with open("cosine.txt", 'a', encoding='utf-8') as f:
        #f.write(term + "\n")
        #for doc_pair, value in cos_list:
            #f.write(doc_pair + " = " + str(value) + "\n")


