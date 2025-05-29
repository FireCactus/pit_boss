from abc import ABC, abstractmethod
from typing import *
import pickle
import asyncio
import os
from player import Player
from utils.Loc import Loc

class ItemRepresentation(NamedTuple):
    emoji: Optional[str]
    picture: Optional[str]

class DepletedItem(Exception):
    pass

class Item(ABC):
    __uuid: str
    __uses_left: int
    __name: str
    __representaion: Representation

    def __init__(self, name: str, representation: ItemRepresentation, uses_left: int = 1) -> None:
        self.__name = name
        self.__representaion = representation
        self.__uses_left = uses_left

        self.__uuid = str(uuid.uuid4())

    def get_filepath(self) -> str:
        return Loc.jar(self.__uuid + ".pkl")
    
    async def save_to_disk(self) -> str:

        filepath: str = self.get_filepath()
        with open(filepath, "wb") as f:
            pickle.dump(self)

        return filepath
    
    def _decrement_uses(self) -> None:
        if self.__uses_left == 0:
            raise DepletedItem()
            
        self.__uses_left -= 1 
    
    @abstractmethod
    def use(self) -> None:
        pass

    async def delete_from_disk(self) -> None:
        os.remove(self.get_filepath())


