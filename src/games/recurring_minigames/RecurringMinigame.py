from abc import ABC, abstractmethod
from typing import *

class RecurringMinigame(ABC):
    _win_amount: int
    _refresh_period_seconds: int

    @abstractmethod
    def _determine_win(self, player_pick: str) -> str:
        '''
            Determine whever the loses wins or draws
        '''
        pass