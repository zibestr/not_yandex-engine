from engine.index import SearchIndex
from engine.query_generator import SearchQueryGenerator
from engine.parser import Parser


class SearchEngine:
    def __init__(self, *urls):
        self.parser = Parser(*urls)
        self.index = SearchIndex(self.parser)
        self.query_generator = SearchQueryGenerator(self.index)

    def handle_query(self, query: str) -> list:
        pass
