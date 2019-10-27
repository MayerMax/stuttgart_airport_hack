from flask import Flask, jsonify, request, json
from elasticsearch import Elasticsearch, helpers

from dialogue_system.manager import DialogueManager
from dialogue_system.queries.text_based import TextQuery

with open('../data/shops.json', 'r') as f:
    data = json.load(f)

es = Elasticsearch()
es.indices.delete(index='shop-index', ignore=[400, 404])

dm = DialogueManager()
user_one = '1'

_ = helpers.bulk(es, data, index='shop-index', doc_type='shop-events')
print('Index is built')

app = Flask(__name__)


@app.route('/send_text', methods=['POST'])
def send_text():
    print(request.data.decode())

    text_query = TextQuery(request.data.decode())
    dm_response = dm.reply(user_one, text_query).to_key_value_format()
    print(dm_response)

    return jsonify(dm_response)


@app.route('/', methods=['GET'])
def index():
    return 'Hello'


if __name__ == '__main__':
    app.run(port=8080, debug=True)
