from enchant.checker import SpellChecker
from flask import render_template, redirect, request, session
from flask import Flask
import enchant
import difflib

from requests import get, post

app = Flask(__name__)
app.config['SECRET_KEY'] = 'not_yandex'


def create_robots():
    robots_minus, robots_plus = [], []
    with open("../engine/robots.txt") as file:
        list_ = list(map(lambda x: x.replace("\n", ''), file.readlines()))
        for i, word in enumerate(list_):
            if word.split()[0] == "-":
                robots_minus.append((i, word.split()[1]))
            else:
                robots_plus.append((i, word.split()[1]))
    return robots_minus, robots_plus


def write_robots():
    list_ = []
    for i in range(session.get('minus')):
        if request.form.get(f'minus{i}') is not None and request.form.get(f'minus{i}') != '':
            list_.append('- ' + request.form.get(f'minus{i}'))
    for i in range(session.get('plus')):
        if request.form.get(f'plus{i}') is not None and request.form.get(f'plus{i}') != '':
            list_.append('+ ' + request.form.get(f'plus{i}'))
    with open("../engine/robots.txt", "w") as file:
        file.write('\n'.join(list_))


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

    if set(text) - set(fixed_text):
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
    list_ = get(f"http://127.0.0.1:5000/api/search/{text}").json()
    return render_template("search_result.html", query=text, results=list_, count=len(list_), helpers=helpers,
                           fix_message=fix_message, fix_text=fix_text)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    url_now = get('http://127.0.0.1:5000/api/change').json()
    if request.method == 'POST':
        write_robots()
        result = post('http://127.0.0.1:5000/api/change', json={'new_url': request.form.get('text')})
        if result.json()['message'] == 'Error':
            return render_template('settings.html', url_now=url_now, error_message="Введите корректную ссылку")
        return redirect('/')
    robots_minus, robots_plus = create_robots()
    session['minus'] = len(robots_minus)
    session['plus'] = len(robots_plus)
    return render_template('settings.html', url_now=url_now, robots_plus=robots_plus,
                           robots_minus=robots_minus)


@app.route('/get_response', methods=['GET', 'POST'])
def documentation():
    if request.method == 'POST':
        if 'num-minus' in request.json:
            session['minus'] += 1
        else:
            session['plus'] += 1
    return request.json


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
