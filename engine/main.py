from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from engine import SearchEngine


app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'not_yandex'
engine = SearchEngine('https://telegram.org/', 'stop_words.txt', 'robots.txt')

parser = reqparse.RequestParser()
parser.add_argument('new_url', required=True, type=str)


class SearchApi(Resource):
    def get(self, text):
        return jsonify(engine.handle_query(text))


class ChangeUrl(Resource):
    def post(self):
        args = parser.parse_args()
        engine.change_url(args['new_url'])

    def get(self):
        return jsonify(engine.parser.main_url)


if __name__ == '__main__':
    api.add_resource(SearchApi, '/api/search/<string:text>')
    api.add_resource(ChangeUrl, '/api/change')
    app.run(port=8080, host='127.0.0.1')