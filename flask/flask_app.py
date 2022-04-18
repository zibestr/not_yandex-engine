from flask import render_template, redirect, request, session
from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'not_yandex'


@app.route('/', methods=['GET', 'POST'])
def index():
    helpers = []
    if 'search' in session:
        helpers = session.get('search')[:10]
    session.permanent = True
    if request.method == 'POST':
        if request.form.get('text'):
            return redirect(f"/search_result/{request.form.get('text')}")
        return render_template("search.html", message="Введите текст")
    return render_template("search.html", helpers=helpers)


@app.route('/search_result/<string:text>')
def search(text):
    if 'search' in session:
        if text not in session.get('search'):
            session['search'].insert(0, text)
    else:
        session['search'] = [text]
    # Короче тут по text находим нужные запросы и выдаёт в итоге список словарей
    # с ключами: название сайта, текст сайта (любой), ссылка сайта
    list_ = [{'title': 'Негры',
              'text': "Длинный текст который, надеюсь будет обрезан. Ведь в гугле было также и если у меня не получится то это будет просто пиздец и с таким проетом мы никогда не сможем выиграть.",
              'href': "http://niggers/buy/man"},
             {'title': 'Помогите', 'text': "Короткий текст", 'href': "https://niggers/buy/woman"}]
    return render_template("search_result.html", query=text, results=list_, count=len(list_))


@app.route('/settings')
def settings():
    return render_template("settings.html")


@app.route('/documentation')
def documentation():
    return render_template("documentation.html")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
