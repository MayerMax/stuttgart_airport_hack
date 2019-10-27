import random
from typing import Dict, Union

from elasticsearch import Elasticsearch

from dialogue_system.actions.abstract import AbstractAction, ActivationResponse
from dialogue_system.queries.text_based import TextQuery
from dialogue_system.responses.image_based import SingleImageResponse
from dialogue_system.responses.text_based import SingleTextResponse
from slots.slot import Slot
from utils import clean_html


class ShopByNameAction(AbstractAction):
    recognized_types = [TextQuery]

    def __init__(self, user_id, props: dict, slots: Dict[Slot, str], es_params: dict = None):
        super().__init__(user_id=user_id, props=props, slots=slots)
        self._es = Elasticsearch() if not es_params else Elasticsearch(es_params)

    @classmethod
    def activation_response(cls, initial_query: TextQuery, slots: Dict[Slot, str]) -> ActivationResponse:
        if Slot.ShopByName not in slots:
            return None
        return ActivationResponse(intent_detected=True)

    def reply(self, slots: Dict[Slot, str], user_id=None) -> Union[SingleTextResponse, SingleImageResponse]:
        shop_name = self._initial_slots[Slot.ShopByName]

        output = self._es.search(index='shop-index', body={
            "query": {
                "match": {
                    "name": {
                        "query": shop_name,
                        "fuzziness": "2"
                    }
                }
            }
        })['hits']['hits'][0]['_source']

        text = f'{output["name"]}, floor: {output["floor"]}, type: {output["type"]}'
        # TODO add description

        if output['image_url']:
            yield SingleImageResponse(is_finished=True, is_successful=True, text=text,
                                      img_url=output['image_url'], img_description='')
        else:
            yield SingleTextResponse(is_finished=True, is_successful=True, text=text)