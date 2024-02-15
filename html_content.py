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
        self.queries.create_postings()

        self.root_dir = root_dir
        self.term_dict = dict()
        self.token_data = []
        self.term_id = 0
        self.alnum_tokenizer = RegexpTokenizer(r"[^\W_]+")
        self.stop_words = set(stopwords.words('english'))
        self.wordnet_lemmatizer = WordNetLemmatizer()

    def get_html_content(self):
        count = -1
        for path, directories, files in os.walk(self.root_dir):
            for file in files:
                if not file.endswith('.json') and not file.endswith('.tsv'):
                    file_path = os.path.join(path, file)

                    # if file_path.startswith("WEBPAGES_RAW\\0\\") or file_path.startswith("WEBPAGES_RAW\\1"):
                    now = datetime.now()
                    time = now.strftime("%H:%M:%S")
                    print(time + " - Handling: " + str(file_path))

                    try:
                        with open(file_path, 'rb') as f:
                            url_data = f.read()
                            tree = html.fromstring(url_data)
                            text = tree.text_content().lower()

                            tokens = self.get_tokens(text)
                            self.hash(tokens.keys())
                            self.add_postings(tokens, file_path)

                            #with open("tokensc.txt", 'w', encoding='utf-8') as ww:
                            #    ww.write(str(self.term_dict))
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
                    now = datetime.now()
                    time = now.strftime("%H:%M:%S")
                    print(time + " - Finishing: " + str(file_path))

            # After 25 files have been processed, transfer to database and reset postings
            count += 1
            if count == 25:
                count = 0
                self.queries.insert_postings(self.term_dict)

        # Transfer all remaining postings after completing all files
        if count != 0:
            now = datetime.now()
            stime = now.strftime("%H:%M:%S")
            self.queries.insert_postings(self.term_dict)
            now = datetime.now()
            time = now.strftime("%H:%M:%S")
            print(" - Start query time: " + stime)
            print(" - End query time: " + time)

        with open("tokens.txt", 'a', encoding='utf-8') as f:
            f.write(str(self.term_dict))
        now = datetime.now()
        time = now.strftime("%H:%M:%S")
        print("Start time: " + self.start_time + "\nEnd time: " + time)

    def get_tokens(self, text):
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
                    if ltoken in tokens:
                        tokens[ltoken] += 1
                    else:
                        tokens[ltoken] = 1

        return tokens

    def add_postings(self, tokens, file_path):
        doc_path = file_path.split(os.path.sep)[-2:]
        doc_name = "/".join(doc_path)

        for token, freq in tokens.items():
            # Adds a tuple of (term_id, document_name, tf-idf)
            # to the postings list of each token found in the files
            self.term_dict[token][1].append((self.term_dict[token][0], doc_name, freq))

    def hash(self, tokens):
        # Adds new term with a tuple of a new unique termID and its postings list
        # { term : (term_id, []) }
        #                     ^ postings list -- postings will be added here
        for token in tokens:
            if token not in self.term_dict:
                self.term_dict[token] = (self.term_id, []) #self.term_id
                self.term_id += 1

    def sort_terms(self):
        sorted_tuple = sorted(self.token_data, key=lambda tuple: tuple[0])
        self.token_data = sorted_tuple

    def is_ascii(self, s):
        try:
            s.encode('ascii')
        except UnicodeEncodeError:
            return False
        else:
            return True




