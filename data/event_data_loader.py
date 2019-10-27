import json

with open('shops.json', 'r') as f:
    data = json.load(f)

from elasticsearch import Elasticsearch, helpers

es = Elasticsearch()
index = helpers.bulk(es, data, index='shop-index', doc_type='shop-events')