import re
import pymorphy2


def edit_string(string):
    pattern = re.compile('[\W_]+')
    return pattern.sub(' ', string)


def morph_word(word):
    morph = pymorphy2.MorphAnalyzer()
    return morph.parse(word)[0].normal_form


def morph_words(words):
    return [morph_word(word) for word in words]


def filter_text(text, stop_words_file='stop_words.txt'):
    text = text.lower()
    text = edit_string(text)
    text = text.split()
    stop_words = make_stop_words(stop_words_file)
    text = morph_words(text)
    text = [word for word in text if word not in stop_words]
    return text


def make_stop_words(stop_words_file):
    with open(stop_words_file, encoding='UTF-8') as file:
        return [word.replace('\n', '') for word in file.readlines()]
