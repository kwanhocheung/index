import os
from lxml import html
import nltk
from nltk.stem import WordNetLemmatizer
from queries import Queries

class content:
    def __init__(self, root_dir, queries):
        self.queries = queries
        self.root_dir = root_dir
        self.hash_term = {}
        self.token_data = []
        self.init = 0

    def get_html_content(self):
        for path, directories, files in os.walk(self.root_dir):
            for file in files:
                if not file.endswith('.json') and not file.endswith('.tsv'):
                    file_path = os.path.join(path, file)
                    try:
                        with open(file_path, 'rb') as f:
                            url_data = f.read()
                            tree = html.fromstring(url_data)
                            content = tree.text_content().lower()
                            token_in_content = self.get_token(content)
                            self.hash(token_in_content)
                            self.token_doc(token_in_content,file_path)
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")


    def get_token(self, content):
        token = []
        each_token = ''
        for each_char in content:
            if each_char.isalnum() and each_char.isascii():
                each_token = each_token + each_char
            elif each_token != '':
                WordNetLemmatizer().lemmatize(each_token)
                token.append(each_token)
                each_token = ''
        if each_token != '':
            token.append(each_token)
        return token

    def token_doc(self, AllToken, file_path):
        doc_path = file_path.split(os.path.sep)[-2:]
        doc_name = "/".join(doc_path)

        for token in AllToken:
            # init tuple
            token_index = [0, 0, 0]
            # assign tuple
            token_index[0] = self.hash_term[token]
            token_index[1] = doc_name
            token_index[2] = AllToken.count(token)
            self.queries.insert_tuple(token_index)
            while token in AllToken:
                AllToken.remove(token)

    def hash(self, AllToken):
        for token in AllToken:
            if token not in self.hash_term:
                self.hash_term[token] = self.init
                self.init += 1
    def query(self,term):
        term_id = self.hash_term
        self.queries.query(term_id, term)




