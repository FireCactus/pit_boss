import discord
import asyncio
import random
import os

from enum import StrEnum, auto
from typing import *
from discord.ext.commands import Context
from discord import File

roulette_gifs_path: str = os.path.join("media", "roulette_gifs")


class RouletteOutcomes(StrEnum):
    GREEN = "green"
    RED = "red"
    BLACK = "black"
    EVEN = "even"
    ODD = "odd"


color_table: dict[int,RouletteOutcomes] ={
    0: RouletteOutcomes.GREEN,
    1: RouletteOutcomes.RED,
    2: RouletteOutcomes.BLACK,
    3: RouletteOutcomes.RED,
    4: RouletteOutcomes.BLACK,
    5: RouletteOutcomes.RED,
    6: RouletteOutcomes.BLACK,
    7: RouletteOutcomes.RED,
    8: RouletteOutcomes.BLACK,
    9: RouletteOutcomes.RED,
    10: RouletteOutcomes.BLACK,
    11: RouletteOutcomes.BLACK,
    12: RouletteOutcomes.RED,
    13: RouletteOutcomes.BLACK,
    14: RouletteOutcomes.RED,
    15: RouletteOutcomes.BLACK,
    16: RouletteOutcomes.RED,
    17: RouletteOutcomes.BLACK,
    18: RouletteOutcomes.RED,
    19: RouletteOutcomes.RED,
    20: RouletteOutcomes.BLACK,
    21: RouletteOutcomes.RED,
    22: RouletteOutcomes.BLACK,
    23: RouletteOutcomes.RED,
    24: RouletteOutcomes.BLACK,
    25: RouletteOutcomes.RED,
    26: RouletteOutcomes.BLACK,
    27: RouletteOutcomes.RED,
    28: RouletteOutcomes.BLACK,
    29: RouletteOutcomes.BLACK,
    30: RouletteOutcomes.RED,
    31: RouletteOutcomes.BLACK,
    32: RouletteOutcomes.RED,
    33: RouletteOutcomes.BLACK,
    34: RouletteOutcomes.RED,
    35: RouletteOutcomes.BLACK,
    36: RouletteOutcomes.RED
} 


class RouletteBet(NamedTuple):
    name: str
    bet_amount: int
    pick: RouletteOutcomes 

class RouletteGame:

    _payout_table: dict[str,float] = {
    "red_black_payout":2.0,
    "even_odd_payout":2.0,
    "correct_green_guess":37.0,
    "green_when_not_chosen":0.5 #when you pick red or black but the roulette comes up green
    }


    def __init__(self, bets: list[RouletteBet]) -> None:
        self.bets: list[RouletteBet] = bets

        self.rolled_number: Optional[int] = None
        self.rolled_color: Optional[RouletteOutcomes] = None
        self.rolled_parity: Optional[RouletteOutcomes] = None

    def spin_the_wheel(self) -> None:
        roulette_pick: int = random.randint(0,36)

        self.rolled_number = roulette_pick
        self.rolled_color = color_table[roulette_pick]
        self.rolled_parity =  RouletteOutcomes.EVEN if roulette_pick % 2 == 0 else RouletteOutcomes.ODD

    
    def calculate_win_amounts(self) -> Dict[str,int]:
        win_dict: Dict[str,int] = {}
        for bet in self.bets:
            if bet.name not in win_dict.keys():
                win_dict[bet.name] = 0

            # if bet on even/odd and was correct
            if bet.pick in [RouletteOutcomes.EVEN, RouletteOutcomes.ODD] and self.rolled_parity == bet.pick:
                win_dict[bet.name] += int(bet.bet_amount * self._payout_table['even_odd_payout'])
            
            # if bet on red/black and was correct
            elif bet.pick in [RouletteOutcomes.RED, RouletteOutcomes.BLACK] and self.rolled_color == bet.pick:
                win_dict[bet.name] += int(bet.bet_amount * self._payout_table['red_black_payout'])

            # if bet on green and was correct
            elif bet.pick == RouletteOutcomes.GREEN and self.rolled_color == bet.pick:
                win_dict[bet.name] += int(bet.bet_amount * self._payout_table['correct_green_guess'])

            # if bet on anything other than green and green was the result
            elif bet.pick != RouletteOutcomes.GREEN and self.rolled_color == RouletteOutcomes.GREEN:
                win_dict[bet.name] += int(bet.bet_amount * self._payout_table['green_when_not_chosen'])
        
        return win_dict
            

