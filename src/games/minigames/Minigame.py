from abc import ABC, abstractmethod
from typing import *
from enum import StrEnum, auto


class GameResult(StrEnum):
    LOSE = auto()
    WIN = auto()
    DRAW = auto()


class MinigameResult(NamedTuple):
    game_result: GameResult
    payout: int


T = TypeVar('T')


class Minigame(ABC, Generic[T]):

    _win_payout: int
    _lose_payout: int

    def __init__(self, win_payout: int, lose_payout: int) -> None:
        self._win_payout = win_payout
        self._lose_payout = lose_payout

    @abstractmethod
    def _determine_win(self, player_pick: T) -> MinigameResult:
        '''
            Determine whever the loses wins or draws
        '''
        pass