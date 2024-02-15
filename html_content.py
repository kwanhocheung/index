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
        for path, directories, files in os.walk(self.root_dir):
            for file in files:
                if not file.endswith('.json') and not file.endswith('.tsv'):
                    file_path = os.path.join(path, file)

                    try:
                        with open(file_path, 'rb') as f:
                            url_data = f.read()
                            tree = html.fromstring(url_data)
                            text = tree.text_content().lower()

                            tokens = self.get_tokens(text)
                            self.hash(tokens.keys())
                            self.token_doc(tokens, file_path)

                            #with open("tokensc.txt", 'w', encoding='utf-8') as ww:
                            #    ww.write(str(self.term_dict))

                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
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
            if self.isEnglish(token):
                ltoken = self.wordnet_lemmatizer.lemmatize(token)
                if ltoken not in self.stop_words:
                    if ltoken in tokens:
                        tokens[ltoken] += 1
                    else:
                        tokens[ltoken] = 1

        return tokens

    def token_doc(self, tokens, file_path):
        doc_path = file_path.split(os.path.sep)[-2:]
        doc_name = "/".join(doc_path)

        for token, freq in tokens.items():
            # Initialize postings
            token_index = [0, 0, 0]

            # Assign values: (term_id, document name, tf-idf)
            token_index[0] = self.term_dict[token]
            token_index[1] = doc_name
            token_index[2] = freq

            self.queries.insert_postings(token_index)
            #while token in tokens:
            #    tokens.remove(token)

    def hash(self, tokens):
        # Adds new term with new unique termID into term_dict
        for token in tokens:
            if token not in self.term_dict:
                self.term_dict[token] = self.term_id
                self.term_id += 1

    def sort_terms(self):
        sorted_tuple = sorted(self.token_data, key=lambda tuple: tuple[0])
        self.token_data = sorted_tuple

    def isEnglish(self, s):
        try:
            s.encode('ascii')
        except UnicodeEncodeError:
            return False
        else:
            return True




