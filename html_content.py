import os
from lxml import html
from nltk.stem import WordNetLemmatizer

class content:
    def __init__(self,root_dir):
        self.root_dir = root_dir

    def get_html_content(self):
        for path, directories, files in os.walk(self.root_dir):
            for file in files:
                if not file.endswith('.json') and not file.endswith('.tsv'):
                    file_path = os.path.join(path, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        html_content = file.read()
                        tree = html.fromstring(html_content)
                        content = tree.text_content().lower()

    def get_token(self,content):
        token = []
        each_token = ''
        for each_char in content:
            if each_char.isalnum() and each_char.isascii():
                each_token = each_token + each_char
            elif each_token != '':
                WordNetLemmatizer.lemmatize(each_token)
                token.append(each_token)
                each_token = ''
        if each_token != '':
            token.append(each_token)
        return token





