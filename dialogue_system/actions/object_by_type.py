from typing import Dict, Union

from elasticsearch import Elasticsearch

from dialogue_system.actions.abstract import AbstractAction, ActivationResponse
from dialogue_system.queries.text_based import TextQuery
from dialogue_system.responses.image_based import SingleImageResponse
from dialogue_system.responses.text_based import SingleTextResponse
from slots.slot import Slot


class ObjectByTypeAction(AbstractAction):
    recognized_types = [TextQuery]

    def __init__(self, user_id, props: dict, slots: Dict[Slot, str], es_params: dict = None):
        super().__init__(user_id=user_id, props=props, slots=slots)
        self._es = Elasticsearch() if not es_params else Elasticsearch(es_params)

    @classmethod
    def activation_response(cls, initial_query: TextQuery, slots: Dict[Slot, str]) -> ActivationResponse:
        if Slot.ObjectType not in slots:
            return None
        return ActivationResponse(intent_detected=True)

    def reply(self, slots: Dict[Slot, str], user_id=None) -> Union[SingleTextResponse, SingleImageResponse]:
        object_type = self._initial_slots[Slot.ObjectType]

        output = self._es.search(index='shop-index', body={
            "query": {
                "match": {
                    "type": {
                        "query": object_type,
                        "fuzziness": "2"
                    }
                }
            }
        })['hits']['hits'][0]['_source']

        text = f'{output["name"]}, floor: {output["floor"]}, type: {output["type"]}'

        if output['image_url']:
            yield SingleImageResponse(is_finished=True, is_successful=True, text=text,
                                      img_url=output['image_url'], img_description='')
        else:
            yield SingleTextResponse(is_finished=True, is_successful=True, text=text)
