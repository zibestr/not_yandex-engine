from engine.utils import morph_word
from engine.exceptions import WrongQueryError


class QueryHandler:
    def __init__(self, query_generator):
        self.index = query_generator.index.total_index

    @staticmethod
    def is_query_language(query: str) -> bool:
        if '{' in query and '\\{' not in query or '}' in query and '\\{' not in query:
            return True
        return False

    def handler_and(self, query: list) -> (list, dict):
        result, rating = [], {}
        if query:
            temp = []
            for word in query:
                if word in self.index.keys():
                    temp.append(set(self.index[word].keys()))
            temp_set = temp[0]
            for i in range(1, len(temp)):
                temp_set = temp_set & temp[i]
            result = list(temp_set)
            rating = {url: len(query) for url in result}
        return result, rating

    def handler_or(self, query: list) -> (list, dict):
        rating, result = {}, []
        if query:
            temp = []
            for word in query:
                if word in self.index.keys():
                    temp.append(set(self.index[word].keys()))
                    for url in self.index[word].keys():
                        if url in rating.keys():
                            rating[url] += 1
                        else:
                            rating[url] = 1
            temp_set = temp[0]
            for url in range(1, len(temp) - 1):
                temp_set += url
            result = list(temp_set)
        return result, rating

    def handler_not(self, query: list) -> (list, dict):
        result, rating = [], {}
        if query:
            for word in self.index.keys():
                if word not in query:
                    for url in self.index[word].keys():
                        if url not in rating.keys() and url not in result:
                            rating[url] = 1
                            result.append(url)
                        elif rating[url] != -1 and url not in result:
                            result.append(url)
                else:
                    for url in (self.index[word].keys()):
                        rating[url] = -1
                    result = list(set(result) - set(self.index.keys()))
        return result, rating

    def handle_query(self, text_query: str) -> (list, list, dict):
        query = Query(text_query)
        result_not, rating_not = self.handler_not(query.not_words)
        result_and, rating_and = self.handler_and(query.and_words)
        result_or, rating_or = self.handler_or(query.or_words)
        result, rating = [], rating_or
        result = list(set(result_or + result_and + result_not))
        for url in rating_and.keys():
            if url in rating.keys():
                rating[url] += rating_and[url]
            else:
                rating[url] = rating_and[url]
        for url in rating_not.keys():
            if url in rating.keys():
                if rating_not[url] == -1:
                    rating[url] = rating_not[url]
                else:
                    rating[url] += rating_not[url]
            else:
                rating[url] = rating_not[url]
        return (list(set(query.and_words + query.or_words + query.not_words)),
                [url for url in result if rating[url] != -1],
                {url: rate for url, rate in rating.items() if rate != -1})


class Query:
    def __init__(self, string: str):
        self.string = string
        self.and_words, self.or_words, self.not_words = [], [], []
        self.parse()

    def parse(self):
        for query in self.string.split():
            if query.startswith('{') and query.endswith('}'):
                query = query.replace('{', '').replace('}', '')
                if '&' in query and '|' in query or \
                        '!' in query and '|' in query or \
                        '!' in query and '&' in query:
                    raise WrongQueryError('Wrong query. '
                                          'Query must be contain '
                                          'only 1 logic operator')
                if '&' in query:
                    self.and_words.extend([morph_word(word).lower()
                                           for word in query.split('&')])
                elif '|' in query:
                    self.or_words.extend([morph_word(word).lower()
                                          for word in query.split('|')])
                elif '!' in query:
                    self.not_words.extend([morph_word(word).lower()
                                           for word in query.split('!')])
                else:
                    raise WrongQueryError('Wrong query. '
                                          'Query must be contain '
                                          'logic operator')
            else:
                raise WrongQueryError('Wrong query. '
                                      'Query must be contain '
                                      'in brackets')
        self.not_words = list(filter(lambda w: w != '', self.not_words))
        self.or_words = list(filter(lambda w: w != '', self.or_words))
        self.and_words = list(filter(lambda w: w != '', self.and_words))
