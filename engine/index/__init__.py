from threading import Thread

import json

import os


class SearchIndex:
    def __init__(self, parser, stop_words):
        self.parser = parser

        self.page_terms = {}
        self.total_index = {}
        self.stop_words = stop_words

        self._sl = {}
        self.save_filename = (self.parser.main_url
                              .replace('https://', '')
                              .replace('http://', '')
                              .replace('/', '')
                              + '.json')

        self.count_pages = 0

    # делает промежуточные хеш таблицы
    def _process_pages(self) -> dict:
        self.parser.get_urls()
        self.page_terms = self.parser.content_dict
        self.count_pages = len(self.page_terms)
        return self.page_terms

    # индексирует один файл
    def _index_one_page(self, terms: list, key: str):
        page_index = {}
        for ind, word in enumerate(terms):
            if word in page_index.keys():
                page_index[word].append(ind)
            else:
                page_index[word] = [ind]
        self._sl[key] = page_index

    # индексирует все файлы
    def _index_all_pages(self):
        self._sl = {}
        index_threads = []
        for key, terms in self.page_terms.items():
            index_threads.append(Thread(target=self._index_one_page,
                                        args=(terms, key)))
        for thread in index_threads:
            thread.start()
        for thread in index_threads:
            thread.join()
        self.page_terms = self._sl

    # формирует окончательный индекс
    def _full_index(self):
        buffer = {}
        for page_url in self.page_terms.keys():
            for word in self.page_terms[page_url].keys():
                if word in buffer.keys():
                    if page_url in buffer[word].keys():
                        (buffer[word][page_url]
                         .extend(self
                                 .page_terms[page_url][word][:]))
                    else:
                        buffer[word][page_url] = (self
                                                  .page_terms[page_url]
                                                  [word])
                else:
                    buffer[word] = {page_url:
                                    self.page_terms[page_url][word]}
        self.total_index = buffer

    # формирует индекс
    def create(self):
        self._process_pages()
        self._index_all_pages()
        self._full_index()

        self.save_index()

    def save_index(self):
        with open('saved indexes/' + self.save_filename,
                  'w', encoding='UTF-8') as save_file:
            json.dump(self.total_index, save_file,
                      indent=4, ensure_ascii=False)

    def load_index(self):
        if self.save_filename in os.listdir('saved indexes'):
            with open('saved indexes/' + self.save_filename,
                      'r', encoding='UTF-8') as load_file:
                self.total_index = json.load(load_file)
            pages = set()
            for value in self.total_index.values():
                for page in value.keys():
                    pages.add(page)
            self.count_pages = len(pages)
        else:
            self.create()
