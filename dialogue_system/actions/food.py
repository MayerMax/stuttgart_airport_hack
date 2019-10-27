import random
from typing import Dict

from elasticsearch import Elasticsearch

from dialogue_system.actions.abstract import AbstractAction
from dialogue_system.queries.text_based import TextQuery
from dialogue_system.responses.abstract import ActivationResponse
from dialogue_system.responses.image_based import MultiImageBasedResponse, SingleImageResponse
from dialogue_system.responses.text_based import SingleTextResponse
from slots.slot import Slot


class FindRestaurantAction(AbstractAction):
    _TRIGGERS_ = ['eat', 'food', 'drinks', 'soft drink', 'hot drink', 'restaurant', 'cafe', 'fast food']
    recognized_types = [TextQuery]

    def __init__(self, user_id, props: dict, slots: Dict[Slot, str], es_params: dict = None):
        super().__init__(user_id=user_id, props=props, slots=slots)
        self._es = Elasticsearch() if not es_params else Elasticsearch(es_params)

    @classmethod
    def activation_response(cls, initial_query: TextQuery, slots: Dict[Slot, str]) -> ActivationResponse:
        for trigger in FindRestaurantAction._TRIGGERS_:
            if trigger in initial_query.text:
                return ActivationResponse(intent_detected=True)

    def reply(self, slots: Dict[Slot, str], user_id=None) -> SingleTextResponse:
        output = self._es.search(index='shop-index', body={
            "query": {
                "match": {
                    "type": {
                        "query": 'food',
                        "fuzziness": "2"
                    }
                }
            }

        })['hits']['hits']
        output = output[0: min(3, len(output))]
        answer = []
        for x in output:
            x = x['_source']
            answer.append(SingleImageResponse(is_finished=True, is_successful=True, text=f'{x["name"]}, '
                                                                                        f'floor: {x["floor"]}, type: {x["type"]}', img_url=x['image_url']))
        yield MultiImageBasedResponse(is_finished=True, is_successful=True,
                                      list_of_single_img_responses=answer)
