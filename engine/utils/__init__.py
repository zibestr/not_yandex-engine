import re
import pymorphy2


def edit_string(string: str) -> str:
    pattern = re.compile('[\W_]+')
    return pattern.sub(' ', string)


def morph_word(word: str) -> str:
    morph = pymorphy2.MorphAnalyzer()
    return morph.parse(word)[0].normal_form


def filter_text(text: str, stop_words: iter) -> iter:
    text = text.lower()
    text = edit_string(text)
    text = map(morph_word, filter(lambda word: word not in stop_words,
                                  text.split()))
    return text
