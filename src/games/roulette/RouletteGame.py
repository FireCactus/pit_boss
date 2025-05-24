import discord
import asyncio
import random
import os

from enum import Enum
from typing import Optional, Literal, NamedTuple
from discord.ext.commands import Context
from discord import File

roulette_gifs_path: str = os.path.join("media", "roulette_gifs")


class RouletteOutcomes(str, Enum):
    GREEN="GREEN"
    RED="RED"
    BLACK="BLACK"
    EVEN="EVEN"
    ODD="ODD"



color_table: dict[int,str] ={
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

    _delete_gif_after_seconds = 10
    _delete_info_after_seconds = 5

    def __init__(self) -> None:
        pass


    async def play(self, ctx: Context, bet_list: list[RouletteBet]) -> dict[str,int]:
        '''
            returns which user and how much should get paid
        '''

        #pick random number
        roulette_pick: int = random.randint(0,36)
        roulette_gif_name: str = f"roulette_{roulette_pick}.gif" 
        roulette_gif_path: str = os.path.join(roulette_gifs_path,roulette_gif_name)

        #send roulette gif
        with open(roulette_gif_path, 'rb') as f:
            gif: File = discord.File(f)
            await ctx.send(file=gif, delete_after=self._delete_gif_after_seconds)


        roulette_color: str = color_table[roulette_pick]
        roulete_even_odd: str = "Even" if roulette_pick % 2 == 0 else "Odd"

        #print roulette result to chat
        await asyncio.sleep(self._delete_gif_after_seconds-3)
        await ctx.send(f"The roulette has stopped!\n Result was: {roulette_pick}-{roulette_color}!", delete_after=self._delete_info_after_seconds)
        
    
        winners_dict: dict[str,int] = {}
        for bet in bet_list:
            winners_dict[bet.name] = 0

        #determine who won and how much to give them
        for bet in bet_list:
            
            # if bet on even/odd and was correct
            if bet.pick in [RouletteOutcomes.EVEN, RouletteOutcomes.ODD] and roulete_even_odd == bet.pick:
                winners_dict[bet.name] += int(bet.bet_amount * self._payout_table['even_odd_payout'])
            
            # if bet on red/black and was correct
            elif bet.pick in [RouletteOutcomes.RED, RouletteOutcomes.BLACK] and roulette_color == bet.pick:
                winners_dict[bet.name] += int(bet.bet_amount * self._payout_table['red_black_payout'])

            # if bet on green and was correct
            elif bet.pick == RouletteOutcomes.GREEN and roulette_color == bet.pick:
                winners_dict[bet.name] += int(bet.bet_amount * self._payout_table['correct_green_guess'])

            # if bet on anything other than green and green was the result
            elif bet.pick != RouletteOutcomes.GREEN and roulette_color == RouletteOutcomes.GREEN:
                winners_dict[bet.name] += int(bet.bet_amount * self._payout_table['green_when_not_chosen'])

        return winners_dict

                