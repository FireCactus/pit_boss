from abc import ABC, abstractmethod
from typing import *
import pickle
import asyncio
import os
import uuid

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
    __description: str
    __representaion: ItemRepresentation

    def __init__(self, name: str, description: str, representation: ItemRepresentation, uses_left: int = 1) -> None:
        self.__name = name
        self.__description = description
        self.__representaion = representation
        self.__uses_left = uses_left

        self.__uuid = str(uuid.uuid4())

    def get_filepath(self) -> str:
        return Loc.jar(self.__uuid + ".pkl")
    
    def save_to_disk(self) -> str:

        filepath: str = self.get_filepath()
        with open(filepath, "wb") as f:
            pickle.dump(self, f)

        return filepath
    
    def _decrement_uses(self) -> None:
        if self.__uses_left == 0:
            raise DepletedItem(f"{self.__name} has no more uses left!")

        self.__uses_left -= 1 

    def get_name(self) -> str:
        return self.__name

    def get_description(self) -> str:
        return self.__description

    def get_uses_left(self) -> int:
        return self.__uses_left

    def get_representation_emoji(self) -> Optional[str]:
        return self.__representaion.emoji

    def get_representation_image(self) -> Optional[str]:
        return self.__representaion.picture

    @abstractmethod
    def use(self) -> None:
        pass

    def delete_from_disk(self) -> None:
        os.remove(self.get_filepath())


