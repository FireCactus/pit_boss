from abc import ABC, abstractmethod
from typing import *
import random


class LootBoxItem(NamedTuple):
    name: str
    probability: float
    amount: int
    item_class: Any


class LootBox(ABC):
    _price: int
    _name: str
    _label: str
    _winnable_items: list[LootBoxItem]

    def __init__(self) -> None:
        self._check_if_item_probabilites_are_valid()

    @final
    def open(self) -> LootBoxItem:
        item_identifier: float = random.random() # 0...1
        current_item: float = 0
        for item in self._winnable_items:
            current_item += item.probability
            if item_identifier <= current_item:
                return item
        raise ValueError("Rank was not chosen! check lootbox rank probabilities!")

    @final
    def _check_if_item_probabilites_are_valid(self) -> None:
        '''
        check if all probabilities add up to 1
        '''
        total: float = 0
        for item in self._winnable_items:
            total += item.probability

        assert total >= 1 and total <= 1.000000002, f"The _winnable_items probabilities do NOT add up to 1 but {total}"
        # floating point math fix
        