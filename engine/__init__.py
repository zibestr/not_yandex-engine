import os

import requests

from engine.exceptions import WrongRobotsFormatError
from engine.index import SearchIndex
from engine.query_generator import SearchQueryGenerator
from engine.parser import Parser


class SearchEngine:
    def __init__(self, url: str, stop_words_file: str, robots_file: str):
        headers = {
            'accept': 'text/html,application/xhtml+xml,'
                      'application/xml;q=0.9,'
                      'image/webp,image/apng,*/*;q=0.8',
            'upgrade-insecure-requests': '1',
            'User-agent': 'Mozilla/5.0'
        }

        with open(f'{os.getcwd()}/{stop_words_file}',
                  encoding='UTF-8') as file:
            self.stop_words = map(lambda word: word.replace('\n', ''),
                                  file.readlines())

        site_exceptions = []
        site_additional = []
        with open(f'{os.getcwd()}/{robots_file}',
                  encoding='UTF-8') as file:
            for line in file.readlines():
                if len(line.split()) > 2 or '-' not in line and '+' not in line:
                    raise WrongRobotsFormatError('Wrong robots.txt format')
                char, page_url = line.replace('\n', '').split()
                if char == '-':
                    site_exceptions.append(page_url)
                elif char == '+':
                    site_additional.append(page_url)

        self.parser = Parser(url, self.stop_words,
                             headers, site_exceptions,
                             site_additional)
        self.index = SearchIndex(self.parser, self.stop_words)

        self.index.load_index()

        self.query_generator = SearchQueryGenerator(self.index,
                                                    self.stop_words)

    def recreate_index(self):
        self.index.create()

    def handle_query(self, text_query: str) -> list:
        return self.make_format_response(self
                                         .query_generator
                                         .handle_query(text_query))

    def change_url(self, url: str):
        self.parser.change_url(url)
        self.index.change_url()

        self.index.load_index()

    def make_format_response(self, results: list) -> list:
        response = []
        for result in results:
            try:
                title, text = self.parser.get_info(result)
            except requests.exceptions.ConnectionError:
                continue
            response.append({'title': title,
                             'text': text,
                             'href': result})
        return response
