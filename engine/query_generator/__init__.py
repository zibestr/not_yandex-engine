from engine.utils import edit_string, morph_word, filter_text
from engine.index import SearchIndex
from engine.query_generator.handler import QueryHandler
from math import log, sqrt


class SearchQueryGenerator:
    def __init__(self, index: SearchIndex, stop_words: iter,
                 range_algorithm: callable = None):
        self.index = index
        if range_algorithm is None:
            self.range_algorithm = self.standard_range
        else:
            self.range_algorithm = range_algorithm
        self.handler = QueryHandler(self)
        self.stop_words = stop_words

    def __one_word_query__(self, word: str) -> list:
        total_index = self.index.total_index
        word = morph_word(edit_string(word))
        if word in total_index.keys():
            return self.index.total_index[word].keys()
        else:
            return []

    def make_query(self, string: str) -> list:
        return filter_text(edit_string(string), self.stop_words)

    def handle_query(self, string: str) -> list:
        if self.handler.is_query_language(string):
            return self.range_algorithm(*self.handler.handle_query(string))
        else:
            return self.range_algorithm(*self.standard_query(string))

    def standard_query(self, string: str) -> (list, list, dict):
        total_index = self.index.total_index
        query_list = list(self.make_query(string))
        list_of_lists, result = [], []
        rating = {}
        for word in query_list:
            list_of_lists.append(self.__one_word_query__(word))
        setted = set(list_of_lists[0]).intersection(*list_of_lists)
        for page in setted:
            temp = []
            for word in query_list:
                temp.append(total_index[word][page][:])
            for i in range(len(temp)):
                for ind in range(len(temp[i])):
                    temp[i][ind] -= i
            if set(temp[0]).intersection(*temp):
                result.append(page)
                rating[page] = len(query_list) + 1
        for response_seq in list_of_lists:
            for page in response_seq:
                if page not in result:
                    rating[page] = 1
                    result.append(page)
                elif rating[page] < len(query_list) + 1:
                    rating[page] += 1
        return query_list, result, rating

    # tf-idf ранжирование + учёт глубины ссылки
    def standard_range(self, query: list, results: list, rating: dict) -> list:
        count_word = {result: 0 for result in results}
        for word in query:
            for result in results:
                if result in self.index.total_index[word]:
                    count_word[result] += len(self.index
                                              .total_index[word][result])
        sum_words = {result: 0 for result in results}
        for value in self.index.total_index.values():
            for page in value:
                if page in results:
                    sum_words[page] += len(page)
        for key in sum_words.keys():
            sum_words[key] = max(sum_words[key], 1)
        rating = {result: rating[result] + (count_word[result] / sum_words[result])
                          * log(self.index.count_pages / len(results))
                          * (4 / sqrt(len(result.split('/'))) + 1)
                  for result in results}
        buffer_list = list(rating.items())
        buffer_list.sort(key=lambda i: -i[1])
        return [pair[0] for pair in buffer_list]
