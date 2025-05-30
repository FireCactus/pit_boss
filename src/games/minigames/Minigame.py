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
    name: str
    discord_id: int


T = TypeVar('T')


class Minigame(ABC, Generic[T]):
    _result: T
    _payout: int

    def __init__(self, _payout: int) -> None:
        self._payout = _payout

    @abstractmethod
    def _determine_results(self, player_pick: T) -> List[MinigameResult]:
        '''
            Determine who wins loses or draws
        '''
        pass