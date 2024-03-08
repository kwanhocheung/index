import os
from lxml import html, etree
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
                            doc_path = file_path.split(os.path.sep)[-2:]
                            doc_name = "/".join(doc_path)

                            tokens = self.get_tokens(tree)
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

    def get_tokens(self, tree):
        # \w --> alphanumeric characters including underscore
        # \W is opposite of \w
        # [^\W_] is looking for characters that are NOT \W and underscore
        ##### alnum_tokenizer = RegexpTokenizer(r"[^\W_]+")
        weight = {"title":15,"h1":10,"h2":5,"h3":4,"h4":3,"h5":2,"h6":1,"strong":2,"b":2,"em":2,"p":7,"a":2,"div": 1,"ul":1,"ol":1,"li":1,"span":1}
        # token: (freq, total_weight)
        tokens = dict()

        # Iterate over all elements
        for tag, weight in weight.items():
            for element in tree.findall('.//{}'.format(tag)):
                text = element.text_content().lower()
                all_tokens = self.alnum_tokenizer.tokenize(text)
                for token in all_tokens:
                    if self.is_ascii(token):
                        ltoken = self.wordnet_lemmatizer.lemmatize(token)
                        if ltoken not in self.stop_words:
                            if ltoken in tokens:
                                freq, current_weight = tokens[ltoken]
                                tokens[ltoken] = (freq + 1, current_weight + weight)
                            else:
                                tokens[ltoken] = (1, weight)
        return tokens

    def add_postings(self, tokens, doc_name):

        for token, freq_weight in tokens.items():
            # Adds a tuple of (term_id, document_name, freq, tf)
            # to the postings list of each token found in the files
            tf = 1 + round(math.log(freq_weight[0]), 4)
            self.term_dict[token][1].append((self.term_dict[token][0], doc_name, freq_weight[0], tf, freq_weight[1]))

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

    def query_get_index(self,term):
        index_list = []
        for each_word in term:
            term_id = self.term_dict[each_word][0]
            index_list.append(self.queries.get_index(term_id))

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
        return dict(sum_by_key)

    def query_get_doc_norm(self, term):
        result_list = []
        length = 0
        for each_word in term:
            term_id = self.term_dict[each_word][0]
            result_list.append(self.queries.get_doc_vector(term_id))
            length += 1

        # break the tuple of list of list to tuple of list
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

            sum_square_of_weight = {}
            for each_tuple in new_result:
                if each_tuple[1] in sum_square_of_weight:
                    sum_square_of_weight[each_tuple[1]] += each_tuple[2] * each_tuple[2]
                else:
                    sum_square_of_weight[each_tuple[1]] = each_tuple[2] * each_tuple[2]
            for doc, value in sum_square_of_weight.items():
                # get the magnitude of the vector
                sum_square_of_weight[doc] = value**0.5

            # store the normalized vector
            result_list = []
            for each_tuple in new_result:
                x = each_tuple[0]
                y = each_tuple[1]
                z = each_tuple[2]/sum_square_of_weight[each_tuple[1]]
                result_list.append((x, y, z))

            del new_result
            sorted_tuple = tuple(sorted(result_list, key=lambda x: x[2],reverse=True))
            return sorted_tuple

        # handle the word only has 1 term
        else:
            sum_square_of_weight = {}
            for each_tuple in flattened:
                sum_square_of_weight[each_tuple[1]] = each_tuple[2] * each_tuple[2]

            for doc, value in sum_square_of_weight.items():
                # get the magnitude of the vector
                sum_square_of_weight[doc] = value**0.5

            new_result = []
            for each_tuple in flattened:
                x = each_tuple[0]
                y = each_tuple[1]
                z = each_tuple[2] / sum_square_of_weight[each_tuple[1]]
                new_result.append((x, y, z))

            del flattened
            sorted_tuple = tuple(sorted(new_result, key=lambda x: x[2], reverse=True))
            # #list
            return sorted_tuple

    def query_get_query_norm(self, term):
        result_list = []
        term_dict = {}
        for each_word in term:
            term_id = self.term_dict[each_word][0]
            result_list.append(self.queries.get_query_vector(term_id))
            if each_word in term_dict:
                term_dict[term_id] += 1
            else:
                term_dict[term_id] = 1

        flattened = sum(result_list, [])
        del result_list
        for each_tuple in flattened:
            tf = term_dict[each_tuple[0]]
            term_dict[each_tuple[0]] = tf*each_tuple[1]

        value = 0
        for doc, tf_idf in term_dict.items():
            value += tf_idf*tf_idf
        magnitude = value**0.5
        for doc, tf_idf in term_dict.items():
            term_dict[doc] = round(tf_idf/magnitude, 4)
        return term_dict

    def get_cosine_similarity(self,term):
        norm_doc = self.query_get_doc_norm(term)
        norm_query = self.query_get_query_norm(term)
        index_dict = self.query_get_index(term)

        multi = []
        for e in norm_doc:
            term_id = e[0]
            doc = e[1]
            norm = e[2]
            multi.append((term_id, doc, round(norm*norm_query[term_id], 4)))
        del norm_doc

        score_dict = {}
        for e in multi:
            if e[1] in score_dict:
                score_dict[e[1]] += e[2]
            else:
                score_dict[e[1]] = e[2]

        top20_score = dict(sorted(score_dict.items(), key=lambda x:x[1], reverse=True)[:20])
        del score_dict

        for key, value in top20_score.items():
            # doc, score, weight(tf_idf+tag_weight), cosine_similarity_score
            print(key+"  score: "+str(value)+"  weight: "+str(index_dict[key][0])+"  "+index_dict[key][1]+"\n")



