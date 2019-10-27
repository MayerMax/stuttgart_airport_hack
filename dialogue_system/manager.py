from typing import Optional
from collections import namedtuple

from dialogue_system.actions.abstract import AbstractAction, DummyHelloAction
from dialogue_system.actions.default_response_action import DefaultAnswerAction
from dialogue_system.actions.food import FindRestaurantAction
from dialogue_system.actions.public_transport import PublicTransportAction
from dialogue_system.actions.rental import RentACarAction
from dialogue_system.actions.search_by_tag import SearchByTagAction
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
        FindRestaurantAction: 0,
        SearchByTagAction: 0,
        RentACarAction: 0,
        PublicTransportAction: 0

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
                                    FindRestaurantAction: self.__find_restaurant_action,
                                    SearchByTagAction: self.__search_by_tag_action,
                                    RentACarAction: self._get_car_rental,
                                    PublicTransportAction: self.__get_public_transport,
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
    def __find_restaurant_action(user_id, props: dict, slots: Dict[Slot, str]):
        return FindRestaurantAction(user_id=user_id, props=props, slots=slots)

    @staticmethod
    def __search_by_tag_action(user_id, props: dict, slots: Dict[Slot, str]):
        return SearchByTagAction(user_id=user_id, props=props, slots=slots)

    @staticmethod
    def _get_car_rental(user_id, props: dict, slots: Dict[Slot, str]):
        return RentACarAction(user_id=user_id, props=props, slots=slots)

    @staticmethod
    def __get_public_transport(user_id, props: dict, slots: Dict[Slot, str]):
        return PublicTransportAction(user_id=user_id, props=props, slots=slots)

    @staticmethod
    def _get_default_response(user_id, props: dict, slots: Dict[Slot, str]):
        return DefaultAnswerAction(user_id=user_id, props=props, slots=slots)


if __name__ == '__main__':
    dm = DialogueManager()
    user_one, user_two = '1', '2'
    # print(dm.reply(user_one, TextQuery('about sbahn')))
    # print(dm.reply(user_one, TextQuery('rent a car')))
    # print(dm.reply(user_one, TextQuery('buy swarowski')))
    # print(dm.reply(user_one, TextQuery('find duty free')))

    print(dm.reply(user_one, TextQuery('fossil shop')))