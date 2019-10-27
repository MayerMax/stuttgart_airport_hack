from typing import Optional
from collections import namedtuple

from dialogue_system.actions.abstract import AbstractAction, DummyHelloAction
from dialogue_system.actions.default_response_action import DefaultAnswerAction
from dialogue_system.actions.object_by_type import ObjectByTypeAction
from dialogue_system.actions.shop_by_name import ShopByNameAction
from dialogue_system.queries.abstract import AbstractQuery
from dialogue_system.queries.text_based import TextQuery
from dialogue_system.responses.abstract import AbstractResponse
from typing import Dict

from slots.slot import Slot
from slots.slots_filler import SlotsFiller

DynamicResponse = namedtuple('DynamicResponse', ['action', 'replier'])


class ActiveUsersManager:
    max_retry_counts = {
        DummyHelloAction: 0,
        ShopByNameAction: 0,
        ObjectByTypeAction: 0
    }

    def __init__(self):
        self._user_action_dict = {}
        self._num_negative_counts_to_call = {}

    def add(self, user_id: int, action: AbstractAction, slots: Dict[Slot, str]) -> AbstractResponse:
        dr = DynamicResponse(action, action.reply(slots, user_id=user_id))
        response: AbstractResponse = next(dr.replier)
        if not response.is_finished:
            self._user_action_dict[user_id] = dr
            self._num_negative_counts_to_call[user_id] = 0
        return response

    def get_response(self, user_id: int, query: AbstractQuery, slots: Dict[Slot, str]) -> Optional[AbstractResponse]:
        response: AbstractResponse = self._user_action_dict[user_id].replier.send((query, slots))

        if response.is_finished:
            self.remove(user_id)
            return response

        if not response.is_successful:
            self._num_negative_counts_to_call[user_id] += 1

        if self._num_negative_counts_to_call[user_id] > self.max_retry_counts[
            type(self._user_action_dict[user_id].action)]:
            self.remove(user_id)
            return None

        return response

    def remove(self, user_id):
        if user_id in self._user_action_dict:
            self._user_action_dict.pop(user_id)
            self._num_negative_counts_to_call.pop(user_id)

    def __contains__(self, user_id: int):
        return user_id in self._user_action_dict


class DialogueManager:
    def __init__(self):
        self._active_users = ActiveUsersManager()
        self._slot_filler = SlotsFiller()

        self._actions_call_order = {DummyHelloAction: self.__dummy_hello_action,
                                    ShopByNameAction: self.__shop_by_name_action,
                                    ObjectByTypeAction: self._object_by_type_action,
                                    DefaultAnswerAction: self._get_default_response}

    def reply(self, user_id: str, query: AbstractQuery) -> AbstractResponse:
        if user_id not in self._active_users:
            return self._active_users.add(user_id,
                                          self.__find_suitable_action(user_id, query),
                                          self._slot_filler.enrich(query))
        else:
            new_slots = self._slot_filler.enrich(query)
            response = self._active_users.get_response(user_id, query, new_slots)
            if not response:
                return self.reply(user_id, query)
            return response

    def __find_suitable_action(self, user_id, query: AbstractQuery) -> AbstractAction:
            slots = self._slot_filler.enrich(query)
            for action_class in self._actions_call_order:
                if type(query) in action_class.recognized_types:
                    activation_response = action_class.activation_response(query, slots)
                    if activation_response:
                        # разные action-ы имеют разные конструкторы
                        return self._actions_call_order[action_class](props=activation_response.props, slots=slots,
                                                                      user_id=user_id)
            return self._actions_call_order[DefaultAnswerAction](props={}, slots={}, user_id=user_id)

    @staticmethod
    def __dummy_hello_action(user_id, props: dict, slots: Dict[Slot, str]):
        return DummyHelloAction(user_id=user_id)

    @staticmethod
    def __shop_by_name_action(user_id, props: dict, slots: Dict[Slot, str]):
        return ShopByNameAction(user_id=user_id, props=props, slots=slots)

    @staticmethod
    def _object_by_type_action(user_id, props: dict, slots: Dict[Slot, str]):
        return ObjectByTypeAction(user_id=user_id, props=props, slots=slots)

    @staticmethod
    def _get_default_response(user_id, props: dict, slots: Dict[Slot, str]):
        return DefaultAnswerAction(user_id=user_id, props=props, slots=slots)


if __name__ == '__main__':
    dm = DialogueManager()
    user_one, user_two = '1', '2'
    print(dm.reply(user_one, TextQuery('where i can find food')))
    # print(dm.reply(user_one, TextQuery('расскажи про Успение Богоматери')))
    # print(dm.reply(user_one, TextQuery('расскажи про девочку на шаре')))
    # print(dm.reply(user_one, TextQuery('как попасть на выставку Русский Йорданс')))
    # print(dm.reply(user_one, TextQuery('когда будет лекция про искусство древней греции')))

    # print(dm.reply(user_one, TextQuery('как попасть в Искусство Древнего Египта?')))
    # print(dm.reply(user_one, TextQuery('греческий дворик')))
    # print(dm.reply(user_one, TextQuery('да')))

    # print(dm.reply(user_one, TextQuery('хочу узнать про пабло пикассо')))

    # print(dm.reply(user_one, TextQuery('хочу найти что-то из алибастра')))
    # print(dm.reply(user_one, TextQuery('расскажи про пушкина')))
    # print(dm.reply(user_one, TextQuery('как проехать до музея?')))
    # print(dm.reply(user_one, TextQuery('красная площадь')))

    # print(dm.reply(user_one, TextQuery('как звали жену Пушкина?')))
    # print(dm.reply(user_two, TextQuery('расскажи про пушкина')))
