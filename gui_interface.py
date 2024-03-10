from PySide6.QtWidgets import QPushButton, QWidget, QLineEdit, QTableWidget, QVBoxLayout, QTableWidgetItem
from PySide6.QtCore import Slot
from html_content import Indexer
from lxml import html
import os

class search_gui(QWidget):
    def __init__(self, indexer) -> None:
        super().__init__()
        self.indexer = indexer

        #set name and layout
        self.setWindowTitle("CS121 Project 3 - Search Engine")
        self.layout = QVBoxLayout()

        #init textbox for user to enter words
        self.input = QLineEdit()
        self.layout.addWidget(self.input)
        
        #initialize search button
        self.button = QPushButton("Search")
        self.button.clicked.connect(self.search)
        self.layout.addWidget(self.button)

        #init result table
        self.result = QTableWidget()
        self.result.setColumnCount(3)
        self.result.setHorizontalHeaderLabels(["Name", "Description", "URL"])
        self.layout.addWidget(self.result)

        self.setLayout(self.layout)

    @Slot()
    def search(self):
        #clear table before every search
        self.clear_table()

        query = self.input.text()
        tokenized_term = self.indexer.alnum_tokenizer.tokenize(query)
        docname_dict = self.indexer.get_cosine_similarity(tokenized_term)

        self.result.setRowCount(len(docname_dict))
        #set title, desc from html content to the results
        row = 0
        for key, value in docname_dict.items():
            #split the folder_name/file_name, then find the file in the root dir
            folder_name = key.split("/")[0]
            file_name = key.split("/")[1]
            file_path = self.find_document_in_folder(self.indexer.root_dir, folder_name, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            #parse with lxml to get the metadata, for its title and description
            html_bytes = html_content.encode('utf-8')
            tree = html.fromstring(html_bytes)

            #get the title name
            title_elements = tree.xpath('//title/text()')
            title = title_elements[0] if title_elements else None
            #get the description
            description_element = tree.find(".//h1")
            description = description_element.text_content().strip() if description_element is not None else None

            title_item = QTableWidgetItem(title)
            desc_item = QTableWidgetItem(description)
            url_item = QTableWidgetItem(value)
            self.result.setItem(row, 0, title_item)
            self.result.setItem(row, 1, desc_item)
            self.result.setItem(row, 2, url_item)
            self.result.resizeColumnsToContents()
            row += 1

    def clear_table(self):
        self.result.clearContents()
        self.result.setRowCount(0)

    def find_document_in_folder(self, root_dir, folder_name, doc_name):
        for folders in os.listdir(root_dir):
            if folders == folder_name:
                folder_path = os.path.join(root_dir, folder_name)
                # Traverse the folder
                for path, directories, files in os.walk(folder_path):
                    for file_name in files:
                        # Check if the file name matches the file key
                        if file_name == doc_name:
                            return os.path.join(path, file_name)
        return None
    