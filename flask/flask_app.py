from enchant.checker import SpellChecker
from flask import render_template, redirect, request, session
from flask import Flask
import enchant
import difflib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'not_yandex'


def create_answers(text):
    # Короче тут по text находим нужные запросы и выдаёт в итоге список словарей
    # с ключами: название сайта, текст сайта (любой), ссылка сайта
    return [{'title': 'Негры',
              'text': "Длинный текст который, надеюсь будет обрезан. Ведь в гугле было также и если у меня не получится то это будет просто пиздец и с таким проетом мы никогда не сможем выиграть.",
              'href': "http://niggers/buy/man"},
             {'title': 'Помогите', 'text': "Короткий текст", 'href': "https://niggers/buy/woman"}]


def create_session(text):
    if 'search' in session:
        if text not in session.get('search'):
            session['search'].insert(0, text)
    else:
        session['search'] = [text]


def get_session(text):
    list_ = []
    if 'search' in session:
        list_ = session.get('search')[:8]
        if text in list_:
            list_.remove(text)
    return list_


def correct_text(text):
    dictionary = enchant.Dict("ru_RU")
    fixed_text = []
    message = []
    text = text.split()
    tag = "/fixed"

    for woi in text:
        if len(woi) == 1:
            fixed_text.append(woi)
        else:
            sim = {}
            suggestions = set(dictionary.suggest(woi))
            for word in suggestions:
                measure = difflib.SequenceMatcher(None, woi, word).ratio()
                sim[measure] = word
            fixed_text.append(sim[max(sim.keys())])

    if not set(text) - set(fixed_text):
        return ' '.join(text), message
    message = [word + tag if word != text[i] else text[i] for i, word in enumerate(fixed_text)]
    return ' '.join(fixed_text), message


@app.route('/', methods=['GET', 'POST'])
def index():
    helpers = get_session('')
    session.permanent = True
    if request.method == 'POST':
        if request.form.get('text'):
            return redirect(f"/search_result/{request.form.get('text')}/1")
        return render_template("search.html", message="Введите текст", helpers=helpers)
    return render_template("search.html", helpers=helpers)


@app.route('/search_result/<string:text>/<int:enable_fix>')
def search(text, enable_fix):
    fix_text, fix_message = text, []
    if enable_fix:
        fix_text, fix_message = correct_text(text)
    text = ' '.join(text.split())
    create_session(text)
    helpers = get_session(text)
    list_ = create_answers(fix_text)
    return render_template("search_result.html", query=text, results=list_, count=len(list_), helpers=helpers,
                           fix_message=fix_message, fix_text=fix_text)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template("settings.html")


@app.route('/documentation')
def documentation():
    return render_template("documentation.html")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
