import os
from lxml import html
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from datetime import datetime
import math
import json


class Indexer:
    def __init__(self, root_dir, queries):
        now = datetime.now()
        time = now.strftime("%H:%M:%S")
        self.start_time = time
        self.queries = queries
        self.queries.create_database()

        self.root_dir = root_dir
        self.term_dict = dict()

        self.term_totalfreq = dict()
        self.total_doc = 0
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

                    # debugging time
                    now = datetime.now()
                    time = now.strftime("%H:%M:%S")
                    print(time + " - Handling: " + str(file_path))

                    try:
                        with open(file_path, 'rb') as f:
                            url_data = f.read()
                            tree = html.fromstring(url_data)
                            # Get doc_name only without parent directory
                            doc_path = file_path.split(os.path.sep)[-2:]
                            doc_name = "/".join(doc_path)

                            tokens = self.get_tokens(tree)      # Get tokens from file
                            self.hash(tokens.keys())            # Create term_dict from tokens
                            self.add_postings(tokens, doc_name) # Add postings to database
                            self.total_doc += 1     # Keeps track of total documents retrieved
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
                    now = datetime.now()
                    time = now.strftime("%H:%M:%S")
                    print(time + " - Finishing: " + str(file_path))

            # After 20 files have been processed, transfer to database and reset postings
            count += 1
            if count == 10:
                count = 0
                self.queries.insert_postings(self.term_dict)

        # Transfer all remaining postings after completing all files
        if count != 0:
            self.queries.insert_postings(self.term_dict)

        # Create idf table for each term
        self.queries.insert_idf(self.term_totalfreq, self.total_doc)
        # Create index_data table for better retrieval
        self.queries.merge_table()
        # Store magnitudes of each document vector : will be used for cosine sim
        mag = self.queries.build_magnitudes()
        with open("magnitudes.json", "w") as outfile:
            json.dump(mag, outfile)
        # Save term: term_id for retrieval use
        with open("term_termId.json", "w") as outfile:
            json.dump(self.term_dict, outfile)

        # Debugging: time of total index creation
        # with open("tokens.txt", 'w', encoding='utf-8') as f:
        #     f.write(str(self.term_dict))
        now = datetime.now()
        time = now.strftime("%H:%M:%S")
        print("Start time: " + self.start_time + "\nEnd time: " + time)

    def get_tokens(self, tree):
        # \w --> alphanumeric characters including underscore
        # \W is opposite of \w
        # [^\W_] is looking for characters that are NOT \W and underscore
        ##### alnum_tokenizer = RegexpTokenizer(r"[^\W_]+")

        # List of weights for different html tags
        weight = {"title":15,"h1":10,"h2":5,"h3":4,"h4":3,"h5":2,"h6":1,"strong":2,"b":2,
                  "em":2,"p":7,"a":2,"div": 1,"ul":1,"ol":1,"li":1,"span":1}

        tokens = dict()
        # Format: {token: (frequency, weight)}

        # Find all tokens under each weight
        for tag, weight in weight.items():
            for element in tree.findall('.//{}'.format(tag)):

                text = element.text_content().lower()
                # Get all tokens from tokenizer
                all_tokens = self.alnum_tokenizer.tokenize(text)

                for token in all_tokens:
                    # Lemmatize each token and check stop words
                    if self.is_ascii(token):
                        ltoken = self.wordnet_lemmatizer.lemmatize(token)
                        if ltoken not in self.stop_words:
                            if ltoken in tokens:
                                # Increase frequency and add weight for token
                                freq, current_weight = tokens[ltoken]
                                tokens[ltoken] = (freq + 1, current_weight + weight)
                            else:
                                tokens[ltoken] = (1, weight)

                # handle 2 gram query
                for i in range(len(all_tokens)-1):
                    if self.is_ascii(all_tokens[i]) and self.is_ascii(all_tokens[i+1]):
                        token_one = self.wordnet_lemmatizer.lemmatize(all_tokens[i])
                        token_two = self.wordnet_lemmatizer.lemmatize(all_tokens[i+1])
                        if token_one not in self.stop_words and token_two not in self.stop_words:
                            two_token = token_one+" "+token_two
                            if two_token in tokens:
                                # Increase frequency and add weight for token
                                freq, current_weight = tokens[two_token]
                                tokens[two_token] = (freq + 1, current_weight + weight)
                            else:
                                tokens[two_token] = (1, weight)

        return tokens

    def add_postings(self, tokens, doc_name):
        for token, freq_weight in tokens.items():
            # Adds a tuple of (term_id, document_name, freq, tf, tag_weight)
            # to the postings list of each token found in the files
            tf = 1 + round(math.log(freq_weight[0]), 4)
            self.term_dict[token][1].append((self.term_dict[token][0], doc_name, freq_weight[0], tf, freq_weight[1]))

            # For every term, add to total frequency in documents
            # Document frequency --> Use for idf calculation
            if self.term_dict[token][0] in self.term_totalfreq:
                self.term_totalfreq[self.term_dict[token][0]] += 1
            else:
                self.term_totalfreq[self.term_dict[token][0]] = 1

    def hash(self, tokens):
        # Adds new term with a tuple of a new unique termID and its postings list
        # { term : (term_id, []) }
        #                     ^ postings list -- postings will be added here
        for token in tokens:
            if token not in self.term_dict:
                self.term_dict[token] = (self.term_id, [])
                self.term_id += 1

    def is_ascii(self, s):
        try:
            s.encode('ascii')
        except UnicodeEncodeError:
            return False
        else:
            return True
