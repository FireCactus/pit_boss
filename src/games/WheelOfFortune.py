import random
from typing import *
class WheelOfFortune:
    _list_of_prizes: List[int]
    def __init__(self) -> None:
        self._list_of_prizes = [-100, -50, -30, 0, 10, 15, 20, 50, 65, 75, 100, 125, 150, 250]
        pass

    def spin(self) -> int:
        random.shuffle(self._list_of_prizes)
        result: int = random.choice(self._list_of_prizes)
        return result