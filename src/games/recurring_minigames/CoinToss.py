import random
from games.recurring_minigames import RecurringMinigame
from typing import *
class CoinTossDaily(RecurringMinigame):

    _options: List[str] 
    def __init__(self) -> None:
        self._options = ["Tails","Heads"]
        self._win_amount = 50
        self._refresh_period_seconds = 60 * 60 * 24 # every day

    def _determine_win(self, player_pick: str) -> str:
        if player_pick not in self._options:
            raise ValueError(f"Player pick is not one of the options, Player picked: {player_pick}, expected {self._options}")
        
        result = random.choice(self._options)
        if result == player_pick:
            return "Win"
        return "Lose"