from typing import *
import random

from games.minigames.Minigame import Minigame, MinigameResult, GameResult

class WheelOfFortune(Minigame[None]):


    _list_of_prizes: List[int]


    def __init__(self, list_of_prizes: Optional[List[int]]) -> None:
            self._list_of_prizes = [-20, -10, -5, 0, 10, 15, 20, 25, 30, 40, 50] if list_of_prizes == None else list_of_prizes
            super().__init__(0, 0)


    def _determine_win(self, player_pick: None) -> int:

        random.shuffle(self._list_of_prizes)
        
        result: int = random.choice(self._list_of_prizes)
        
        if result == 0:
            return MinigameResult(GameResult.DRAW, result)
        elif result > 0:
            return MinigameResult(GameResult.WIN, result)
        
        return MinigameResult(GameResult.LOSE, result)