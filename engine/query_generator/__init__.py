from engine.utils import edit_string, morph_word, morph_words, filter_text
from engine.index import SearchIndex
from engine.query_generator.handler import QueryHandler


class SearchQueryGenerator:
    def __init__(self, index: SearchIndex, range_algorithm: callable = None):
        self.index = index
        if range_algorithm is None:
            self.range_algorithm = self.standard_range
        else:
            self.range_algorithm = range_algorithm
        self.handler = QueryHandler()

    def __one_word_query__(self, word: str) -> list:
        total_index = self.index.total_index
        word = morph_word(edit_string(word))
        if word in total_index.keys():
            return [filename for filename in self.index.total_index[word].keys()]
        else:
            return []

    @staticmethod
    def make_query(string: str) -> list:
        return morph_words(filter_text(edit_string(string)))

    def phrase_query(self, string: str) -> list:
        total_index = self.index.total_index
        query_list = self.make_query(string)
        list_of_lists, result = [], []
        for word in query_list:
            list_of_lists.append(self.__one_word_query__(word))
        setted = set(list_of_lists[0]).intersection(*list_of_lists)
        for filename in setted:
            temp = []
            for word in query_list:
                temp.append(total_index[word][filename][:])
            for i in range(len(temp)):
                for ind in range(len(temp[i])):
                    temp[i][ind] -= i
            if set(temp[0]).intersection(*temp):
                result.append(filename)
        return self.range_algorithm(query_list, result)

    # ранжирование результатов на основе частоты вхождения слов
    def standard_range(self, query: list, results: list) -> list:
        rating = {result: 0 for result in results}
        for word in query:
            for result in results:
                if result in self.index.total_index[word]:
                    rating[result] += len(self.index.total_index[word][result])
        buffer_list = list(rating.items())
        buffer_list.sort(key=lambda i: -i[1])
        return [pair[0] for pair in buffer_list]
