from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from engine import SearchEngine
import requests


app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'not_yandex'
engine = SearchEngine('https://newgramm.pythonanywhere.com/', 'engine/stop_words.txt', 'engine/robots.txt')

parser = reqparse.RequestParser()
parser.add_argument('new_url', required=True, type=str)


class SearchApi(Resource):
    def get(self, text):
        return jsonify(engine.handle_query(text))


class ChangeUrl(Resource):
    def post(self):
        args = parser.parse_args()
        new_url = args['new_url']
        try:
            request = requests.get(new_url)
        except:
            return jsonify({"message": "Error"})
        engine.change_url(new_url)
        return jsonify({"message": "Successful"})

    def get(self):
        return jsonify(engine.parser.main_url)


if __name__ == '__main__':
    api.add_resource(SearchApi, '/api/search/<string:text>')
    api.add_resource(ChangeUrl, '/api/change')
    app.run(port=5000, host='127.0.0.1')
