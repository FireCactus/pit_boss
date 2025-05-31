from abc import ABC, abstractmethod
from typing import *
from player.Item import Item, ItemRepresentation

class CasualItemUsage(NamedTuple):
    returned_string: str


class CasualItem(Item, ABC):
    
    def __init__(self, name: str, description: str, representation: ItemRepresentation):
        super().__init__(name, description, representation)
    
    @abstractmethod
    def use() -> CasualItemUsage:
        pass