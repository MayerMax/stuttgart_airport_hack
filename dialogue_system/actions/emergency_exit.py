from typing import Dict

from dialogue_system.actions.abstract import AbstractAction
from dialogue_system.queries.image import ImageQuery
from dialogue_system.queries.text_based import TextQuery
from dialogue_system.responses.abstract import ActivationResponse
from dialogue_system.responses.text_based import SingleTextResponse
from slots.slot import Slot


class EmergencyAction(AbstractAction):
    _TRIGGERS_ = ['emergency exit', 'emergency']
    recognized_types = [TextQuery]

    @classmethod
    def activation_response(cls, initial_query: TextQuery, slots: Dict[Slot, str]) -> ActivationResponse:
        for trigger in EmergencyAction._TRIGGERS_:
            if trigger in initial_query.text:
                return ActivationResponse(intent_detected=True)

    def reply(self, slots: Dict[Slot, str], user_id=None) -> SingleTextResponse:
        yield SingleTextResponse(is_finished=True, is_successful=True, text='Emergency path is available, open AR and follow the guide')