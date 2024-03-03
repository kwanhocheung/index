import os
from lxml import html
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from datetime import datetime


class Indexer:
    def __init__(self, root_dir, queries):
        now = datetime.now()
        time = now.strftime("%H:%M:%S")
        self.start_time = time
        self.queries = queries
        self.root_dir = root_dir
        # term: term_id, [posting]
        self.term_dict = dict()
        # doc_name: total terms
        self.doc_TotalTerms = dict()
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
        with open("doc_TotalTerms.txt",'a',encoding='utf-8') as f:
            f.write(str(self.doc_TotalTerms))
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
                    # count total tokens in a doc
                    if doc_name in self.doc_TotalTerms:
                        self.doc_TotalTerms[doc_name] += 1
                    else:
                        self.doc_TotalTerms[doc_name] = 1
                    # count each token frequency
                    if ltoken in tokens:
                        tokens[ltoken] += 1
                    else:
                        tokens[ltoken] = 1

        return tokens

    def add_postings(self, tokens, doc_name):

        for token, freq in tokens.items():
            # Adds a tuple of (term_id, document_name, freq)
            # to the postings list of each token found in the files
            total_term_in_a_doc = self.doc_TotalTerms[doc_name]
            tf = round(freq/total_term_in_a_doc, 4)
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

    def query(self, term):
        term_id = self.term_dict[term][0]
        # return set of urls for a term
        return self.queries.query_geturls(term_id)
