import os
from lxml import html
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from datetime import datetime
import math


class Indexer:
    def __init__(self, root_dir, queries):
        now = datetime.now()
        time = now.strftime("%H:%M:%S")
        self.start_time = time
        self.queries = queries
        self.root_dir = root_dir
        # term: term_id, [posting]
        self.term_dict = dict()
        # term_id: df
        self.term_totalfreq = dict()
        self.term_id = 0
        self.total_doc = 0
        self.alnum_tokenizer = RegexpTokenizer(r"[^\W_]+")
        self.stop_words = set(stopwords.words('english'))
        self.wordnet_lemmatizer = WordNetLemmatizer()

    def get_html_content(self):
        self.queries.create_table()
        count = -1
        for path, directories, files in os.walk(self.root_dir):
            for file in files:
                if not file.endswith('.json') and not file.endswith('.tsv'):
                    file_path = os.path.join(path, file)

                    now = datetime.now()
                    time = now.strftime("%H:%M:%S")
                    print(time + " - Handling: " + str(file_path))

                    try:
                        with open(file_path, 'rb') as f:
                            url_data = f.read()
                            tree = html.fromstring(url_data)
                            text = tree.text_content().lower()
                            doc_path = file_path.split(os.path.sep)[-2:]
                            doc_name = "/".join(doc_path)

                            tokens = self.get_tokens(text,doc_name)
                            self.hash(tokens.keys())
                            self.add_postings(tokens, doc_name)
                            self.total_doc += 1
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
                    now = datetime.now()
                    time = now.strftime("%H:%M:%S")
                    print(time + " - Finishing: " + str(file_path))

                    # After 20 files have been processed, transfer to database and reset postings
            count += 1
            if count == 20:
                count = 0
                self.queries.insert_postings(self.term_dict)

                # Transfer all remaining postings after completing all files
        if count != 0:
            self.queries.insert_postings(self.term_dict)
            self.queries.insert_idf(self.term_totalfreq, self.total_doc)
            self.queries.merge_table()

        with open("tokens.txt", 'a', encoding='utf-8') as f:
            f.write(str(self.term_dict))
        now = datetime.now()
        time = now.strftime("%H:%M:%S")
        print("Start time: " + self.start_time + "\nEnd time: " + time)

    def get_tokens(self, text, doc_name):
        # \w --> alphanumeric characters including underscore
        # \W is opposite of \w
        # [^\W_] is looking for characters that are NOT \W and underscore
        ##### alnum_tokenizer = RegexpTokenizer(r"[^\W_]+")

        # Get tokens in text
        all_tokens = self.alnum_tokenizer.tokenize(text)

        tokens = dict()
        #### stop_words = set(stopwords.words('english'))  # List of stop words

        # Lemmatize each token and check stop words
        for token in all_tokens:
            if self.is_ascii(token):
                ltoken = self.wordnet_lemmatizer.lemmatize(token)
                if ltoken not in self.stop_words:
                    # count each token frequency
                    if ltoken in tokens:
                        tokens[ltoken] += 1
                    else:
                        tokens[ltoken] = 1

        return tokens

    def add_postings(self, tokens, doc_name):

        for token, freq in tokens.items():
            # Adds a tuple of (term_id, document_name, freq, tf)
            # to the postings list of each token found in the files
            tf = 1 + round(math.log(freq), 4)
            self.term_dict[token][1].append((self.term_dict[token][0], doc_name, freq, tf))

            # self.term_dict[token][0] return the term id
            if self.term_dict[token][0] in self.term_totalfreq:
                self.term_totalfreq[self.term_dict[token][0]] += 1
            else:
                self.term_totalfreq[self.term_dict[token][0]] = 1

    def hash(self, tokens):
        # Adds new term with new unique termID into term_dict
        for token in tokens:
            if token not in self.term_dict:
                self.term_dict[token] = (self.term_id, [])  # self.term_id
                self.term_id += 1

    def is_ascii(self, s):
        try:
            s.encode('ascii')
        except UnicodeEncodeError:
            return False
        else:
            return True

    # return set of urls for a term
    def query_get_all_urls(self, term):
        urls_list = []
        x = [1125,8862,15,16]
        for each_word in x:
            term_id = self.term_dict[each_word][0]
            urls_list.append(self.queries.get_urls(term_id))

        # if the term more than 1 words
        if len(urls_list) > 1:
            # find commom url from sets of list
            common_urls = urls_list[0]
            for s in urls_list[1:]:
                common_urls = common_urls & s
        else:
            common_urls = urls_list[0]
        del urls_list
        return common_urls

    def query_get_index(self,term):
        index_list = []
        x = [1125, 8862, 15, 16]
        for each_word in x:
            #term_id = self.term_dict[each_word][0]
            index_list.append(self.queries.get_index(each_word))

        # break the tuple of list of list to tuple of list
        flattened = sum(index_list, [])
        sum_by_key = {}
        if len(index_list) > 1:
            # store the documents occurrences
            doc_occurrences = {}
            for each_tuple in flattened:
                if each_tuple[0] in doc_occurrences:
                    doc_occurrences[each_tuple[0]] += 1
                else:
                    doc_occurrences[each_tuple[0]] = 1

            # find common documents, and sum the total tf_idf in sum_by_key dictionary
            for each_tuple in flattened:
                if doc_occurrences[each_tuple[0]] == len(index_list):
                    if each_tuple[0] in sum_by_key:
                        value = sum_by_key[each_tuple[0]][0]
                        sum_by_key[each_tuple[0]] = (value + each_tuple[1], each_tuple[2])
                    else:
                        sum_by_key[each_tuple[0]] = (each_tuple[1], each_tuple[2])
        else:
            for each_tuple in flattened:
                sum_by_key[each_tuple[0]] = (each_tuple[1], each_tuple[2])
        del index_list
        return sum_by_key

    def query_get_score(self, term):
        result_list = []
        x = [1125, 8862, 15, 16]
        length = 0
        for each_word in x:
            #term_id = self.term_dict[each_word][0]
            result_list.append(self.queries.get_score(each_word))
            length += 1

        # break the pair of list of list to pair of list
        flattened = sum(result_list, [])
        # reserve more space for memory
        del result_list

        # handle the word more than 1 term
        if length > 1:
            # store the documents occurrences.
            doc_occurrences = {}
            for each_tuple in flattened:
                if each_tuple[1] in doc_occurrences:
                    doc_occurrences[each_tuple[1]] += 1
                else:
                    doc_occurrences[each_tuple[1]] = 1

            new_result = []
            for each_tuple in flattened:
                if doc_occurrences[each_tuple[1]] == length:
                    # add tuple to new_result that match the occurrences. if a term has 2 words, a doc has 2 occurrence
                    new_result.append(each_tuple)
            # reserve more space for memory
            del flattened

            sum_square_of_tf = {}
            for each_tuple in new_result:
                if each_tuple[1] in sum_square_of_tf:
                    sum_square_of_tf[each_tuple[1]] += each_tuple[2] * each_tuple[2]
                else:
                    sum_square_of_tf[each_tuple[1]] = each_tuple[2] * each_tuple[2]
            for doc, value in sum_square_of_tf.items():
                # get the magnitude of the vector
                sum_square_of_tf[doc] = value**0.5

            # store the normalized vector
            result_list = []
            for each_tuple in new_result:
                x = each_tuple[0]
                y = each_tuple[1]
                z = each_tuple[2]/sum_square_of_tf[each_tuple[1]]
                result_list.append((x, y, z))

            del new_result

            cos_dict = {}
            length = len(result_list)
            for i in range(0, length-1):
                for j in range(i+1, length):
                    if result_list[i][0] == result_list[j][0]:
                        doc_pair = result_list[i][1] + "," + result_list[j][1]
                        score = round(result_list[i][2] * result_list[j][2], 4)
                        if doc_pair in cos_dict:
                            cos_dict[doc_pair] += score
                        else:
                            cos_dict[doc_pair] = score

            # return a list of tuple, only top 20
            return sorted(cos_dict.items(), key=lambda x: x[1], reverse=True)

        # handle the word only has 1 term
        else:
            sum_square_of_tf = {}
            for each_tuple in flattened:
                sum_square_of_tf[each_tuple[1]] = each_tuple[2] * each_tuple[2]

            for doc, value in sum_square_of_tf.items():
                # get the magnitude of the vector
                sum_square_of_tf[doc] = value**0.5

            new_result = []
            for each_tuple in flattened:
                x = each_tuple[0]
                y = each_tuple[1]
                z = each_tuple[2] / sum_square_of_tf[each_tuple[1]]
                new_result.append((x, y, z))
            del flattened

            cos_dict = {}
            length = len(new_result)
            for i in range(0, length - 1):
                for j in range(i+1, length):
                    doc_pair = new_result[i][1] + "," + new_result[j][1]
                    score = round(new_result[i][2] * new_result[j][2], 4)
                    cos_dict[doc_pair] = score

            # return a list of tuple, only top 20
            return sorted(cos_dict.items(), key=lambda x: x[1], reverse=True)




