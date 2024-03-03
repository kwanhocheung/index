from html_content import Indexer
import sys
from queries import Queries


if __name__ == "__main__":
    queries = Queries()
    indexer = Indexer(sys.argv[1],queries)
    indexer.get_html_content()
    word_list = ["artificial intelligence computer science"]
    for word in word_list:
        urls_list = []
        index_list = []
        x = indexer.alnum_tokenizer.tokenize(word)
        for each_word in x:
            # append each set of urls to a list
            urls_list.append(indexer.query(each_word))
            index_list.append(indexer.Query(each_word))

        # find common urls from more than 1 set
        if len(urls_list) > 1:
            common_urls = urls_list[0]
            for s in urls_list[1:]:
                common_urls = common_urls & s
        else:
            common_urls = urls_list[0]
        common_urls = list(common_urls)[:20]
        with open("urls.txt", 'a', encoding='utf-8') as f:
            f.write(word+"\n")
            for row in common_urls:
                f.write(row + "\n")
        #
        #
        sum_by_key = {}
        if len(index_list) > 1:
            flattened = sum(index_list,[])
            doc_occurrences = {}
            for key, value in flattened:
                if key in doc_occurrences:
                    doc_occurrences[key] += 1
                else:
                    doc_occurrences[key] = 1

            for key, value in flattened:
                if doc_occurrences[key] == len(index_list):
                    if key in sum_by_key:
                        sum_by_key[key] += value
                    else:
                        sum_by_key[key] = value
        else:
            flattened = sum(index_list, [])
            for key, value in flattened:
                sum_by_key[key] = value
        with open("index.txt", 'a', encoding='utf-8') as f:
            f.write(word+"\n")
            for doc, total_tf_idf in sum_by_key.items():
                f.write(doc + ": " + str(total_tf_idf) + "\n")



