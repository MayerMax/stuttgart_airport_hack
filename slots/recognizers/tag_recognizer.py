import typing
from elasticsearch import Elasticsearch

from dialogue_system.queries.text_based import TextQuery
from slots.recognizers.abstract import AbstractSlotRecognizer
from slots.slot import Slot


class TagRecognizer(AbstractSlotRecognizer):
    recognized_types = [TextQuery]

    def __init__(self):
        self._es = Elasticsearch()

    def recognize(self, query: TextQuery) -> typing.Dict[Slot, str]:
        output = self._es.search(index='shop-index', body={
            "query": {
                "match": {
                    "tags": {
                        "query": query.text,
                        "fuzziness": "2"
                    }
                }
            }
        })['hits']['hits']
        if not output:
            return {}
        output = [x for x in output if x['_score'] > 2.5]
        if not output:
            return {}
        return {Slot.SlotByTag: output}
