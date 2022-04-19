import os

from engine.exceptions import WrongRobotsFormatError
from engine.index import SearchIndex
from engine.query_generator import SearchQueryGenerator
from engine.parser import Parser


class SearchEngine:
    def __init__(self, url, stop_words_file, robots_file):
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
        self.query_generator = SearchQueryGenerator(self.index,
                                                    self.stop_words)

        self.index.load_index()

    def recreate_index(self):
        self.index.create()

    def handle_query(self, text_query: str) -> list:
        return self.make_format_response(self
                                         .query_generator
                                         .phrase_query(text_query))

    def make_format_response(self, results: list) -> list:
        response = []
        for result in results:
            title, text = self.parser.get_info(result)
            response.append({'title': title,
                             'text': text,
                             'href': result})
        return response


if __name__ == '__main__':
    engine = SearchEngine('https://telegram.org/', 'stop_words.txt', 'robots.txt')
    print(engine.handle_query('мессенджер'))
