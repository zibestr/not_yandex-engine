import re
import os
import pymorphy2


class SearchIndex:
    def __init__(self):
        self.stop_words_file = 'stop_words.txt'
        self.files_directory = 'files/'
        self.filenames = []
        self.read_files()

        self.file_terms = {}
        self.total_index = {}

    # переводит слова в именительный падеж
    @staticmethod
    def morph_text(text):
        morph = pymorphy2.MorphAnalyzer()
        return [morph.parse(word)[0].normal_form for word in text]

    # фильтрует базар
    def filter_text(self, text):
        text = text.lower()
        pattern = re.compile('[\W_]+')
        text = pattern.sub(' ', text)
        text = text.split()
        stop_words = self.make_stop_words()
        text = self.morph_text(text)
        text = [word for word in text if word not in stop_words]
        return text

    # делает промежуточные хеш таблицы
    def process_files(self):
        for file in self.filenames:
            with open(f'{self.files_directory}/{file}', encoding='UTF-8') as file_text:
                self.file_terms[file] = self.filter_text(file_text.read())
        return self.file_terms

    # индексирует один файл
    @staticmethod
    def index_one_file(terms):
        file_index = {}
        for index, word in enumerate(terms):
            if word in file_index.keys():
                file_index[word].append(index)
            else:
                file_index[word] = [index]
        return file_index

    # индексирует все файлы
    def index_all_files(self):
        sl = {}
        for key, terms in self.file_terms.items():
            sl[key] = self.index_one_file(terms)
        self.file_terms = sl

    # формирует окончательный индекс
    def full_index(self):
        for filename in self.file_terms.keys():
            for word in self.file_terms[filename].keys():
                if word in self.total_index.keys():
                    if filename in self.total_index[word].keys():
                        self.total_index[word][filename].extend(self.file_terms[filename][word][:])
                    else:
                        self.total_index[word][filename] = self.file_terms[filename][word]
                else:
                    self.total_index[word] = {filename: self.file_terms[filename][word]}

    # загружает стоп слова
    def make_stop_words(self):
        with open(self.stop_words_file, encoding='UTF-8') as file:
            return [word.replace('\n', '') for word in file.readlines()]

    # находит все файлы для поиска
    def read_files(self):
        files = os.listdir(self.files_directory)
        self.filenames = files

    # формирует индекс
    def create(self):
        self.process_files()
        self.index_all_files()
        self.full_index()


search = SearchIndex()
search.create()
print(search.total_index)
