import os
from time import sleep
from engine.utils import filter_text
import threading


class SearchIndex:
    def __init__(self, parser):
        self.parser = parser
        self.stop_words_file = 'stop_words.txt'
        self.files_directory = 'files/'
        self.filenames = []

        self.file_terms = {}
        self.total_index = {}

    # устанавливает директорию файлов
    def set_directory(self, directory):
        self.files_directory = directory

    # делает промежуточные хеш таблицы
    def _process_files(self):
        for file in self.filenames:
            with open(file, encoding='UTF-8') as file_text:
                self.file_terms[file] = filter_text(file_text.read(), stop_words_file=self.stop_words_file)
        return self.file_terms

    # индексирует один файл
    @staticmethod
    def _index_one_file(terms):
        file_index = {}
        for index, word in enumerate(terms):
            if word in file_index.keys():
                file_index[word].append(index)
            else:
                file_index[word] = [index]
        return file_index

    # индексирует все файлы
    def _index_all_files(self):
        sl = {}
        for key, terms in self.file_terms.items():
            sl[key] = self._index_one_file(terms)
        self.file_terms = sl

    # формирует окончательный индекс
    def _full_index(self):
        buffer = {}
        for filename in self.file_terms.keys():
            for word in self.file_terms[filename].keys():
                if word in buffer.keys():
                    if filename in buffer[word].keys():
                        buffer[word][filename].extend(self.file_terms[filename][word][:])
                    else:
                        buffer[word][filename] = self.file_terms[filename][word]
                else:
                    buffer[word] = {filename: self.file_terms[filename][word]}
        self.total_index = buffer

    # добавляет файлы для поиска
    def add_files(self, directory):
        files = os.listdir(directory)
        files = [f'{directory}/{file}' for file in files]
        self.filenames.extend(files)

    # формирует индекс
    def _create(self):
        self._process_files()
        self._index_all_files()
        self._full_index()

    def update_observer_index(self):
        while True:
            sleep(5)
            self._create()

    def run(self):
        self._create()
        index_thread = threading.Thread(target=self.update_observer_index, daemon=True)
        index_thread.start()
