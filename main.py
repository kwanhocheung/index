from html_content import Indexer
import sys
from queries import Queries


if __name__ == "__main__":
    queries = Queries()
    indexer = Indexer(sys.argv[1],queries)
    indexer.get_html_content()
    word_list = ["artificial intelligence", "computer science"]
    for word in word_list:
        urls_list = []
        x = indexer.alnum_tokenizer.tokenize(word)
        for each_word in x:
            # append each set of urls to a list
            urls_list.append(indexer.query(each_word))
        # find common urls from more than 1 set
        if len(urls_list) > 1:
            common_urls = urls_list[0]
            for s in urls_list[1:]:
                common_urls = common_urls & s
        else:
            common_urls = urls_list[0]

        common_urls = list(common_urls)[:20]

        with open("query.txt", 'a', encoding='utf-8') as f:
            f.write(word+"\n")
            for row in common_urls:
                f.write(row + "\n")





