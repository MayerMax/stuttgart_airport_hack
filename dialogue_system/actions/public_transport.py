from typing import Dict

from dialogue_system.actions.abstract import AbstractAction
from dialogue_system.queries.text_based import TextQuery
from dialogue_system.responses.abstract import ActivationResponse
from dialogue_system.responses.text_based import SingleTextResponse
from slots.slot import Slot


class PublicTransportAction(AbstractAction):
    _TRIGGERS_ = ['public transport', 'subway', 'bahn', 'sbahn', 's-bahn', 'train']
    recognized_types = [TextQuery]

    @classmethod
    def activation_response(cls, initial_query: TextQuery, slots: Dict[Slot, str]) -> ActivationResponse:
        for trigger in PublicTransportAction._TRIGGERS_:
            if trigger in initial_query.text:
                return ActivationResponse(intent_detected=True)

    def reply(self, slots: Dict[Slot, str], user_id=None) -> SingleTextResponse:
        yield SingleTextResponse(is_finished=True, is_successful=True,
                                 text='Following directions are the most popular, choose one and proceed:\n'
                                      'S2 From Stuttgart Airport to Stuttgart Central Station will arrive in 7 minutes\n'
                                      'S3 From Stuttgart Airport to Maubach Station will arrive in 22 minutes')
