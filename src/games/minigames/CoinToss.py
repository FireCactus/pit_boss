import random
from typing import *
from enum import Enum, auto

from games.minigames.Minigame import Minigame, GameResult, MinigameResult


class HT(Enum):
    HEAD = "Head"
    TAIL = "Tail"


class CoinTossDaily(Minigame[HT]):


    def __init__(self, win_payout: int, lose_payout: int) -> None:
        super().__init__(win_payout, lose_payout)


    def _determine_win(self, player_pick: HT) -> str:
        
        result: HT = random.choice(list(HT))

        if result == player_pick:
            return MinigameResult(GameResult.WIN, self._win_payout)
        
        return MinigameResult(GameResult.LOSE, self._lose_payout)