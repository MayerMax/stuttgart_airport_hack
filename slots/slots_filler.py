from dialogue_system.queries.abstract import AbstractQuery
from slots.recognizers.fuzzy_text_recognizer import FuzzyTextRecognizer
from slots.slot import Slot


class SlotsFiller:
    def __init__(self):
        self._available_recognizers = [
            FuzzyTextRecognizer(search_slot=Slot.ShopByName,
                                min_threshold=4.5, index_name='shop-index'),
            FuzzyTextRecognizer(search_slot=Slot.ObjectType,
                                min_threshold=2.2, index_name='shop-index'),
        ]

    def enrich(self, query: AbstractQuery, previous_slots=None):
        extracted_slots = previous_slots if previous_slots else {}
        for recognizer in self._available_recognizers:
            if type(query) in recognizer.recognized_types:
                extracted_slots.update(recognizer.recognize(query))
        return extracted_slots
