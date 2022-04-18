from flask import Flask

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    return "Привет, Яндекс!"


@app.route('/search_result')
def search():
    return "Привет, Яндекс!"


@app.route('/settings')
def settings():
    return "Привет, Яндекс!"


@app.route('/documentation')
def documentation():
    return "Привет, Яндекс!"


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
