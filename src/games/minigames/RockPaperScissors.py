from typing import *
import random
from enum import Enum, auto

from games.minigames.Minigame import Minigame, MinigameResult, GameResult


class RPS(Enum):
    ROCK = "Rock"
    PAPER = "Paper"
    SCISSORS= "Scissors"


class RockPaperScissors(Minigame[RPS]):
    

    def __init__(self, win_payout: int, lose_payout: int) -> None:
        super().__init__(win_payout, lose_payout)


    def _determine_win(self, player_pick: RPS) -> MinigameResult:

        result: RPS = random.choice(list(RPS))

        if result == player_pick:
            return MinigameResult(GameResult.DRAW, 0)
            
        wins_against: Dict[RPS, RPS] = {
            RPS.ROCK: RPS.SCISSORS,
            RPS.PAPER: RPS.ROCK,
            RPS.SCISSORS: RPS.PAPER,
        }

        if wins_against[player_pick] == result:
            return MinigameResult(GameResult.WIN, self._win_payout)
        
        return MinigameResult(GameResult.LOSE, self._lose_payout)
