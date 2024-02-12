import os
from lxml import html
import nltk
from nltk.stem import WordNetLemmatizer

class content:
    def __init__(self,root_dir):
        self.root_dir = root_dir

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
                            self.token_indexing(self.get_token(content),file_path)
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
    def get_token(self,content):
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

    def token_indexing(self,AllToken,file_path):
        token_index = {}
        doc_path = file_path.split(os.path.sep)[-2:]
        doc = "/".join(doc_path)
        for token in AllToken:
            if token not in token_index:
                token_index[token] = doc
        with open("index.txt", 'a', encoding='utf-8') as f:
            for key,value in token_index.items():
                f.write(key + " " + str(value) + "\n")






