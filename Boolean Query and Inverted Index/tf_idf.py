import copy
import sys

doc_dict = {}


# manipulating the document object to calculate the term frequencies and removing duplicates
def get_term_tf_dict(doc):
    term_tf_dict = {}
    total_terms_in_doc = len(doc)

    for term in doc:
        if term in term_tf_dict:
            term_tf_dict[term] += 1
        else:
            term_tf_dict[term] = 1

    for term in term_tf_dict:
        # calculating tf using the formula:
        # TF(t) = (Number of times term t appears in a document) / (Total number of terms in the document).
        term_tf_dict[term] = term_tf_dict[term] / total_terms_in_doc

    return term_tf_dict


def sort(query_token_list):
    temp_list = copy.deepcopy(query_token_list)

    for i in range(len(temp_list)):
        for j in range(0, len(temp_list) - i - 1):
            if temp_list[j]['document_freq'] > temp_list[j + 1]['document_freq']:
                temp_list[j]['document_freq'], temp_list[j + 1]['document_freq'] = \
                    temp_list[j + 1]['document_freq'], temp_list[j]['document_freq']

    return temp_list


# classes to implement linked list for postings lists
class Node:

    def __init__(self, data, nextNode: object = None):
        self.data = data
        self.nextNode = nextNode

    def get_data(self):
        return self.data

    def set_data(self, val):
        self.data = val

    def get_next_node(self):
        return self.nextNode

    def set_next_node(self, val):
        self.nextNode = val


class LinkedList:

    def __init__(self, head=None):
        self.head = head
        self.size = 0

    def get_size(self):
        return self.size

    # adding a new posting in the postings list in sorted manner (sorted by doc_id)
    def add_node(self, data):
        curr = self.head
        if curr is None:
            newNode = Node(data, self.head)
            self.head = newNode
            self.size += 1
            return True

        if curr.data['doc_id'] > data['doc_id']:
            newNode = Node(data, self.head)
            self.head = newNode
            self.size += 1
            return True

        while curr.nextNode is not None:
            if curr.nextNode.data['doc_id'] > data['doc_id']:
                break
            curr = curr.nextNode
        newNode = Node(data, curr.nextNode)
        curr.nextNode = newNode
        return True

    def find_node(self):
        curr = self.head
        postings_list = []
        while curr is not None:
            posting = curr.data['doc_id']
            postings_list.append(posting)
            curr = curr.nextNode
        return postings_list

    def find_node_with_doc_id(self, doc_id):
        curr = self.head
        while curr is not None:
            if curr.data['doc_id'] == doc_id:
                return curr.data
            curr = curr.nextNode
        return None


# Intersecting two postings lists at a time
def intersection(postings_list1, postings_list2):
    merged_list = LinkedList()
    pl1 = copy.deepcopy(postings_list1)
    pl2 = copy.deepcopy(postings_list2)
    comparisons = 0

    if pl1 is not None and pl2 is not None:
        p1 = pl1.head
        p2 = pl2.head

        while p1 and p2:
            if p1.data['doc_id'] == p2.data['doc_id']:
                merged_list.add_node(p1.data)
                p1 = p1.nextNode
                p2 = p2.nextNode

            elif p1.data['doc_id'] < p2.data['doc_id']:
                p1 = p1.nextNode

            else:
                p2 = p2.nextNode

            comparisons += 1
    return merged_list, comparisons


# Union of two postings lists at a time
def union(postings_list1, postings_list2):
    merged_list = LinkedList()
    pl1 = copy.deepcopy(postings_list1)
    pl2 = copy.deepcopy(postings_list2)
    comparisons = 0

    if pl1 is not None and pl2 is not None:
        p1 = pl1.head
        p2 = pl2.head

        while p1 and p2:
            if p1.data['doc_id'] == p2.data['doc_id']:
                merged_list.add_node(p1.data)
                p1 = p1.nextNode
                p2 = p2.nextNode

            elif p1.data['doc_id'] < p2.data['doc_id']:
                merged_list.add_node(p1.data)
                p1 = p1.nextNode

            else:
                merged_list.add_node(p2.data)
                p2 = p2.nextNode

            comparisons += 1

        if p1 and not p2:
            while p1:
                merged_list.add_node(p1.data)
                p1 = p1.nextNode

        elif p2 and not p1:
            while p2:
                merged_list.add_node(p2.data)
                p2 = p2.nextNode

    return merged_list, comparisons


# method to create the inverted index
def create_inverted_index(doc_dict):
    # creating the dictionary and postings lists from doc_dict
    term_dictionary = {}
    for doc_id in doc_dict.keys():
        doc = doc_dict[doc_id]
        term_dict_with_tf = get_term_tf_dict(doc)

        for term in term_dict_with_tf:
            term = term.replace('\t', ' ').replace('\n', '').replace(' ', '')
            if term not in term_dictionary:
                term_dictionary[term] = {'document_freq': 0, 'postings_list': LinkedList()}
                term_obj = term_dictionary[term]
                tf_doc_id_node = {'tf': term_dict_with_tf[term], 'doc_id': doc_id}
                term_obj['postings_list'].add_node(tf_doc_id_node)
                term_obj['document_freq'] += 1

            elif term in term_dictionary and doc_id not in term_dictionary[term]:
                term_obj = term_dictionary[term]
                tf_doc_id_node = {'tf': term_dict_with_tf[term], 'doc_id': doc_id}
                term_obj['postings_list'].add_node(tf_doc_id_node)
                term_obj['document_freq'] += 1

    return term_dictionary


# Method to retrieve the postings lists for each of the given query terms
def GetPostings(query, inverted_index):
    query_tokens = query.split()

    for i in range(0, len(query_tokens)):
        posting_list_str = ""
        token = query_tokens[i].replace('\t', ' ').replace('\n', '').replace(' ', '')
        write_file("GetPostings")
        write_file(token)

        postings_linked_list = get_postings_list_for_term(token, inverted_index)
        if postings_linked_list:
            postings_list = postings_linked_list.find_node()
            for posting in postings_list:
                posting_list_str = posting_list_str + " " + str(posting)

            if posting_list_str == "" or posting_list_str == " ":
                posting_list_str = "empty"

            write_file("Postings list: " + posting_list_str)
        else:
            write_file("Postings list: empty")


def get_postings_list_for_term(token, inverted_index):
    if token in inverted_index.keys():
        token_obj = inverted_index[token]
        postings_linked_list = token_obj['postings_list']

    return postings_linked_list


def DaatAnd(query, inverted_index):
    merged_list = None
    total_comparisons = 0
    query_token_list = get_sorted_query_token_list(query, inverted_index)

    if len(query_token_list) == 1:
        query = query.replace('\t', ' ').replace('\n', '').replace(' ', '')
        merged_list = get_postings_list_for_term(query, inverted_index)
    else:
        for i in range(1, len(query_token_list)):
            if merged_list:
                merged_list, comparisons = intersection(merged_list, query_token_list[i]['postings_list'])
                total_comparisons += comparisons
            else:
                merged_list, comparisons = intersection(query_token_list[i - 1]['postings_list'],
                                                        query_token_list[i]['postings_list'])
                total_comparisons += comparisons

    return merged_list, total_comparisons


def DaatOr(query, inverted_index):
    merged_list = None
    total_comparisons = 0
    query_token_list = get_sorted_query_token_list(query, inverted_index)

    if len(query_token_list) == 1:
        query = query.replace('\t', ' ').replace('\n', '').replace(' ', '')
        merged_list = get_postings_list_for_term(query, inverted_index)
    else:
        for i in range(1, len(query_token_list)):
            if query_token_list[i]['postings_list'] is not None:
                if merged_list:
                    merged_list, comparisons = union(merged_list, query_token_list[i]['postings_list'])
                    total_comparisons += comparisons
                else:
                    merged_list, comparisons = union(query_token_list[i - 1]['postings_list'],
                                                     query_token_list[i]['postings_list'])
                    total_comparisons += comparisons

    return merged_list, total_comparisons


def tfidf(query, merged_list, inverted_index, total_docs):
    query_token_idf_list = {}
    doc_score_dict = {}
    query_tokens = query.split()

    for token in query_tokens:
        token = token.replace('\t', ' ').replace('\n', '').replace(' ', '')
        if token in inverted_index.keys():
            token_obj = inverted_index[token]
            idf = total_docs / token_obj['document_freq']
            query_token_idf_list[token] = idf

    if len(merged_list) > 0:
        for doc_obj in merged_list:
            doc_id = doc_obj['doc_id']
            total_score = 0.0
            for term in doc_dict[doc_id]:
                tf_idf = 0.0
                if term in query_token_idf_list and term in inverted_index:
                    term_obj = inverted_index[term]
                    postings_list = term_obj['postings_list']
                    doc_node = postings_list.find_node_with_doc_id(doc_id)
                    if doc_node:
                        tf = doc_node['tf']
                        idf = query_token_idf_list[term]
                        tf_idf = float(tf * idf)
                    total_score = float(total_score + tf_idf)
                doc_score_dict[doc_id] = total_score

    # sorting the documents according to their tf_idf scores
    sorted_list = sorted(doc_score_dict.items(), key=lambda kv: kv[1], reverse=True)
    sorted_doc_list = []
    for item in sorted_list:
        sorted_doc_list.append(item[0])

    return sorted_doc_list


# this method breaks the query into term lists and returns the sorted list based on the doc frequency
def get_sorted_query_token_list(query, inverted_index):
    query_tokens = query.split()
    query_token_list = []

    for i in range(0, len(query_tokens)):
        token = query_tokens[i].replace('\t', ' ').replace('\n', '').replace(' ', '')
        if token in inverted_index.keys():
            query_token_list.append(inverted_index[token])
        else:
            query_token_list.append({'document_freq': 0, 'postings_list': None})

    # sort the terms according to their doc freq
    query_token_list = sort(query_token_list)

    return query_token_list


def print_results(query, merged_list, total_comparisons, tf_idf_sorted_list, func_name):
    posting_list_str = ""
    curr = merged_list.head
    total_docs = 0
    tf_idf_sorted_doc_list_str = ""

    while curr:
        posting_list_str += " " + str(curr.data['doc_id'])
        total_docs += 1
        curr = curr.nextNode

    if posting_list_str == "" or posting_list_str == " ":
        posting_list_str = "empty"

    for doc_id in tf_idf_sorted_list:
        tf_idf_sorted_doc_list_str += " " + str(doc_id)

    if tf_idf_sorted_doc_list_str == "" or tf_idf_sorted_doc_list_str == " ":
        tf_idf_sorted_doc_list_str = "empty"

    write_file(func_name)
    write_file(query)
    write_file("Results: " + posting_list_str)
    write_file("Number of documents in results: " + str(total_docs))
    write_file("Number of comparisons: " + str(total_comparisons))
    write_file("TF-IDF")
    write_file("Results: " + tf_idf_sorted_doc_list_str)


def write_file(output_str):
    filename_op = sys.argv[2]
    # filename_op = "output.txt"

    with open(filename_op, 'a') as f_out:
        if f_out:
            f_out.writelines(output_str + "\n")


def convert_linked_list_to_list(linked_list):
    final_list = []
    if linked_list:
        curr = linked_list.head
    while curr:
        final_list.append(curr.data)
        curr = curr.nextNode
    return final_list


def main():
    # Reading the input corpus
    filename_corpus = sys.argv[1]
    # filename_corpus = "Project2_Dryrun_Corpus.txt"
    with open(filename_corpus, "r") as f:
        for line in f:
            document = line.split()
            key = document[0]
            document = document[1:]
            doc_dict[key] = document

    # total no. of documents
    total_docs = len(doc_dict)

    # creating the inverted index
    inverted_index = create_inverted_index(doc_dict)

    # reading the query from file
    filename_ip_q = sys.argv[3]
    # filename_ip_q = "Project2_Dryrun_input.txt"
    with open(filename_ip_q, "r") as fq:
        for line in fq:
            query = line
            query = query.replace('\n', '')

            # get the postings list for the query terms
            GetPostings(query, inverted_index)
            # DaatAnd Query Processing
            merged_list_and, total_comparisons = DaatAnd(query, inverted_index)
            # tf-idf - AND Query
            and_merged_list = convert_linked_list_to_list(merged_list_and)
            tfidf_sorted_list_and = tfidf(query, and_merged_list, inverted_index, total_docs)
            print_results(query, merged_list_and, total_comparisons, tfidf_sorted_list_and, "DaatAnd")

            # DaatOr Query Processing
            merged_list_or, total_comparisons = DaatOr(query, inverted_index)
            # tf-idf - OR Query
            or_merged_list = convert_linked_list_to_list(merged_list_or)
            tfidf_sorted_list_or = tfidf(query, or_merged_list, inverted_index, total_docs)
            print_results(query, merged_list_or, total_comparisons, tfidf_sorted_list_or, "DaatOr")
            write_file("")


if __name__ == "__main__":
    main()
