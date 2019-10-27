from typing import Dict, Union
from dialogue_system.actions.abstract import AbstractAction, ActivationResponse
from dialogue_system.queries.text_based import TextQuery
from dialogue_system.responses.image_based import SingleImageResponse, MultiImageBasedResponse
from dialogue_system.responses.text_based import SingleTextResponse
from slots.slot import Slot


class SearchByTagAction(AbstractAction):
    recognized_types = [TextQuery]

    def __init__(self, user_id, props: dict, slots: Dict[Slot, str], es_params: dict = None):
        super().__init__(user_id=user_id, props=props, slots=slots)

    @classmethod
    def activation_response(cls, initial_query: TextQuery, slots: Dict[Slot, str]) -> ActivationResponse:
        if Slot.SlotByTag not in slots:
            return None
        return ActivationResponse(intent_detected=True)

    def reply(self, slots: Dict[Slot, str], user_id=None) -> Union[SingleTextResponse, SingleImageResponse]:
        output = self._initial_slots[Slot.SlotByTag]
        output = output[0: min(3, len(output))]

        answer = []
        for x in output:
            x = x['_source']
            answer.append(SingleImageResponse(is_finished=True, is_successful=True, text=f'{x["name"]}, '
                                                                                        f'floor: {x["floor"]}, type: {x["type"]}', img_url=x['image_url']))
        yield MultiImageBasedResponse(is_finished=True, is_successful=True,
                                      list_of_single_img_responses=answer)