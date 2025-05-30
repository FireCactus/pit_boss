import random
from typing import *
from enum import Enum, auto

from games.minigames.Minigame import Minigame, GameResult, MinigameResult




class HT(Enum):
    HEADS = "Heads"
    TAILS = "Tails"

class CoinTossBet(NamedTuple):
    name: str
    discord_id:int
    pick: HT 

class CoinTossDaily(Minigame[HT]):

    def __init__(self, _payout: int) -> None:
        super().__init__(_payout)
        self._result: Optional[HT] = None
        

    def _determine_results(self, bets: List[CoinTossBet]) -> List[MinigameResult]:
        
        self._result = random.choice([HT.HEADS,HT.TAILS])
        game_results: List[MinigameResult] = []
        for bet in bets:
            if self._result == bet.pick:
                game_results.append(MinigameResult(GameResult.WIN, self._payout, bet.name, bet.discord_id))
            else:
                game_results.append(MinigameResult(GameResult.LOSE, 0 , bet.name, bet.discord_id))

        return game_results