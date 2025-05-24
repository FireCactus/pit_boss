import discord
import asyncio
import random
import os

from typing import Optional, Literal, NamedTuple
from discord.ext.commands import Context
from discord import File

roulette_gifs_path: str = os.path.join("media", "roulette_gifs")
roulette_outcomes: list[str] = ["Green", "Red", "Black", "Even", "Odd"]

color_table: dict[int,str] ={
    0: "Green",
    1: "Red",
    2: "Black",
    3: "Red",
    4: "Black",
    5: "Red",
    6: "Black",
    7: "Red",
    8: "Black",
    9: "Red",
    10: "Black",
    11: "Black",
    12: "Red",
    13: "Black",
    14: "Red",
    15: "Black",
    16: "Red",
    17: "Black",
    18: "Red",
    19: "Red",
    20: "Black",
    21: "Red",
    22: "Black",
    23: "Red",
    24: "Black",
    25: "Red",
    26: "Black",
    27: "Red",
    28: "Black",
    29: "Black",
    30: "Red",
    31: "Black",
    32: "Red",
    33: "Black",
    34: "Red",
    35: "Black",
    36: "Red"
} 


class RouletteBet(NamedTuple):
    name: str
    bet_amount: int
    pick: Literal["Green", "Red", "Black", "Even", "Odd"] # mypy does not support dynamic unpacking of lists so need to do this


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
        roulette_gif_name: str = "roulette_{roulette_pick}.gif" 
        roulette_gif_path: str = os.path.join(roulette_gifs_path,roulette_gif_name)

        #send roulette gif
        with open(roulette_gif_path, 'rb') as f:
            gif: File = discord.File(f)
            await ctx.send(file=gif, delete_after=self._delete_gif_after_seconds)


        roulette_color: str = color_table[roulette_pick]
        roulete_even_odd: str = "Even" if roulette_pick % 2 == 0 else "Odd"

        #print roulette result to chat
        await ctx.send(f"The roulette has stopped!\n Result was: {roulette_pick}-{roulette_color}!", delete_after=self._delete_info_after_seconds)
        
    
        winners_dict: dict[str,int] = {}
        for bet in bet_list:
            winners_dict[bet.name] = 0

        #determine who won and how much to give them
        for bet in bet_list:
            
            # if bet on even/odd and was correct
            if bet.pick in ["Even", "Odd"] and roulete_even_odd == bet.pick:
                winners_dict[bet.name] += int(bet.bet_amount * self._payout_table['even_odd_payout'])
            
            # if bet on red/black and was correct
            elif bet.pick in ["Red", "Black"] and roulette_color == bet.pick:
                winners_dict[bet.name] += int(bet.bet_amount * self._payout_table['red_black_payout'])

            # if bet on green and was correct
            elif bet.pick == "Green" and roulette_color == bet.pick:
                winners_dict[bet.name] += int(bet.bet_amount * self._payout_table['correct_green_guess'])

            # if bet on anything other than green and green was the result
            elif bet.pick != "Green" and roulette_color == "Green":
                winners_dict[bet.name] += int(bet.bet_amount * self._payout_table['green_when_not_chosen'])

        return winners_dict

                