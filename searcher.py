from nltk.tokenize import RegexpTokenizer
from datetime import datetime
import json


class Searcher:
    def __init__(self, term_dict, queries, magnitudes):
        self.term_dict = term_dict
        self.queries = queries
        self.magnitudes = magnitudes
        self.alnum_tokenizer = RegexpTokenizer(r"[^\W_]+")

    def start_search(self):
        search = input("SEARCH: ").lower()
        while search != "!q":
            #term = "artificial intelligence computer science"
            #term = "computer"


            now = datetime.now()
            start_time = now.strftime("%H:%M:%S")

            tokenized_term = self.alnum_tokenizer.tokenize(search)
            self.get_cosine_similarity(tokenized_term)

            now = datetime.now()
            time = now.strftime("%H:%M:%S")
            print("Start time: " + start_time + "\nEnd time: " + time + "\n")

            search = input("SEARCH: ").lower()

    def query_get_index(self, term):
        index_list = []
        for each_word in term:
            # Find term_id corresponding to term and
            # return all docs with term
            term_id = self.term_dict[each_word][0]
            index_list.append(self.queries.get_index(term_id))  # (doc_name, weight, url)

        # Combine elements into single list
        flattened = sum(index_list, [])

        sum_by_key = {}
        if len(index_list) > 1:
            # Store the number of occurrences of doc_name
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
        term_ids = []
        length = 0
        for each_word in term:
            # Get term_ids and keeps track of # of terms
            if each_word in self.term_dict.keys():
                term_ids.append(self.term_dict[each_word][0])
                length += 1
        # handle 2 gram query
        for i in range(len(term) - 1):
            two_word = term[i]+" "+term[i+1]
            if two_word in self.term_dict.keys():
                term_ids.append(self.term_dict[two_word][0])
                length += 1

        # Return all docs associated with terms
        docs = self.queries.get_doc_vector(term_ids) # (term_id, doc_name, weight)

        # Handle queries with more the 1 term
        #if length > 1:
        # Store the number of occurrences of doc_name
        doc_occurrences = {}
        for each_tuple in docs:
            if each_tuple[1] in doc_occurrences:
                doc_occurrences[each_tuple[1]] += 1
            else:
                doc_occurrences[each_tuple[1]] = 1

        needed_docs = set()
        new_result = []
        for each_tuple in docs:
            # Add posting if the document occurs at least (length - 1) times
                # If length == doc_occurrences then the doc has all n = length terms in it
            # Index Elimination: doc has to have at least n-1 terms
            if doc_occurrences[each_tuple[1]] >= (length - 1):
                new_result.append(each_tuple)
                needed_docs.add(each_tuple[1])
        # reserve more space for memory
        del docs

        # Get magnitudes for needed documents
        #magnitudes = self.queries.get_magnitudes(needed_docs)

        # Store normalized document vectors
        result_list = []
        for each_tuple in new_result:
            x = each_tuple[0]   # term_id
            y = each_tuple[1]   # doc_name
            z = each_tuple[2] / self.magnitudes[each_tuple[1]]  # Normalized weight
            result_list.append((x, y, z))

        del new_result
        return result_list

    def query_get_query_norm(self, term):
        term_ids = []
        term_dict = {}
        for each_word in term:
            # Find term_ids
            if each_word in self.term_dict.keys():
                term_id = self.term_dict[each_word][0]
                term_ids.append(term_id)

                # Calculate tf for each query term; checking repeated terms
                if each_word in term_dict:
                    term_dict[term_id] += 1
                else:
                    term_dict[term_id] = 1
        # handle 2 gram query
        for i in range(len(term) - 1):
            two_word = term[i]+" "+term[i+1]
            # Find term_ids
            if two_word in self.term_dict.keys():
                term_id = self.term_dict[two_word][0]
                term_ids.append(term_id)

                # Calculate tf for each query term; checking repeated terms
                if two_word in term_dict:
                    term_dict[term_id] += 1
                else:
                    term_dict[term_id] = 1

        # Return idf values for each term
        idfs = self.queries.get_query_vector(term_ids)

        # Calculate tf-idf weight
        for each_tuple in idfs:
            tf = term_dict[each_tuple[0]]
            term_dict[each_tuple[0]] = tf * each_tuple[1]

        # Calculate query magnitude
        value = 0
        for _, tf_idf in term_dict.items():
            value += tf_idf * tf_idf    # sum the square of tf_idf weights
        magnitude = value ** 0.5    # square root the sum

        # Normalize weights for each term
        for term_id, tf_idf in term_dict.items():
            term_dict[term_id] = round(tf_idf / magnitude, 4)
        return term_dict

    def get_cosine_similarity(self, term):
        norm_doc = self.query_get_doc_norm(term)        # List of documents and their normalized weights
        norm_query = self.query_get_query_norm(term)    # Query vector
        # index_dict = self.query_get_index(term)         # Doc weights and URLs

        multi = []
        for e in norm_doc:
            term_id = e[0]
            doc = e[1]
            norm = e[2]
            # Multiply normalized weight of doc with normalized weight of query for the term_id
            multi.append((term_id, doc, round(norm * norm_query[term_id], 4)))
        del norm_doc

        score_dict = {}
        # Add all multiplied query * doc terms for each document
        # Dot product
        for e in multi:
            if e[1] in score_dict:
                score_dict[e[1]] += e[2]
            else:
                score_dict[e[1]] = e[2]

        # Sort by descending scores
        top20_score = dict(sorted(score_dict.items(), key=lambda x: x[1], reverse=True)[:20])
        del score_dict

        # Get doc_name : url
        urls = dict()
        with open("WEBPAGES_RAW\\bookkeeping.json") as file:
            urls = json.load(file)

        """for key, value in top20_score.items():
            # doc, score, weight(tf_idf+tag_weight), cosine_similarity_score
            print("Doc: " + key + ",  Score: " + str(value) + ",  weight: " + str(index_dict[key][0]) + ",  URL: " + index_dict[key][1] + "\n")"""

        # Print results
        for key, value in top20_score.items():
            # doc, score, cosine_similarity_score
            print("Doc: " + key + ",  Score: " + str(value) + ",  URL: " + urls[key])