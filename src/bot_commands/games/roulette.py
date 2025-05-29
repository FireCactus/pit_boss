from discord import Message, User
from discord.ext import commands
from discord.ext.commands import Context, Bot
from typing import *
import asyncio
import os

from player.Player import Player
from games.roulette.RouletteGame import RouletteGame, RouletteBet, RouletteOutcomes
from bot_commands import discord_utilities as du 

odd_reaction: str = "1️⃣"
even_reaction: str = "2️⃣"
black_reaction: str = "⬛"
red_reaction: str = "🟥"
green_reaction: str = "🟩"

roulette_reactions: list[str] = [
    green_reaction,
    black_reaction,
    red_reaction,
    even_reaction,
    odd_reaction,
]

start_game_countdown:int = 6 # how long to wait before starting a game
delete_roulette_gif_after = 10

roulette_gifs_path: str = os.path.join("media", "roulette_gifs")

def setup(bot: Bot) -> None:

    @bot.command("roulette")
    async def roulette_start(ctx: Context, started_by_user: bool = True) -> None:

        if started_by_user:
            await du.delete_message(ctx.message)

        start_text: str = f"Spinning Roulette wheel in {start_game_countdown} seconds!\nPlace your bets!"
        bets: list[RouletteBet] = []
        reaction_users: Dict[User, list[str]] = await du.send_standard_join_game_message(ctx, start_text, roulette_reactions, start_game_countdown)
        for user, reactions in reaction_users.items():
            player = Player(user)
            bet: int = player.get_player_bet()
            for reaction in reactions:
                balance: int = player.get_balance()          

                if bet > balance:
                    poor_text = f"Sorry {player.display_name} You have only {balance}, but you bet {bet}.\nChange your bet size using !bet size [amount]"
                    await du.send_vanishing_message(ctx, poor_text)
                    continue

                if reaction not in roulette_reactions:
                    continue

                player.modify_balance(-bet)
                pick: RouletteOutcomes
                if reaction == odd_reaction:
                    pick = RouletteOutcomes.ODD
                        
                elif reaction == even_reaction:
                    pick = RouletteOutcomes.EVEN
                    
                elif reaction == red_reaction:
                    pick = RouletteOutcomes.RED
                                
                elif reaction == green_reaction:
                    pick = RouletteOutcomes.GREEN            
                
                elif reaction == black_reaction:
                    pick = RouletteOutcomes.BLACK
                
                rt_bet: RouletteBet = RouletteBet(name=player.display_name, discord_id=player.discord_id, bet_amount=bet, pick=pick)
                bets.append(rt_bet)
        
        if len(bets) == 0:
            await du.send_vanishing_message(ctx, "Noone place a bet :(")
            return None
            
        
        # print the bets
        string: str = "----------------------------------------\n"
        for rt_bet in bets:
            string += f"       {rt_bet.name} bet: {rt_bet.bet_amount} on {rt_bet.pick.value}\n"

        await du.send_persistant_message(ctx, string)
        game: RouletteGame = RouletteGame(bets)
        game.spin_the_wheel()

        #send the roulette gif
        roulette_gif_name: str = f"roulette_{game.rolled_number}.gif"
        roulette_gif_path: str = os.path.join(roulette_gifs_path,roulette_gif_name)
        await du.send_vanishing_file_by_path(ctx, roulette_gif_path, delete_roulette_gif_after)
        await asyncio.sleep(delete_roulette_gif_after-2)

        #Print the result
        string = "----------------------------------------\n"
        string += f"The Roulette wheel has stopped!\n Result was: {game.rolled_number} {game.rolled_color.title()}\n"
        
        #pay the winners
        win_dict: Dict[int,int] = game.calculate_win_amounts()
        string += "---------- Roulette Results ----------"
        for discord_id, amount in win_dict.items():
            player = Player(await du.get_discord_user_from_id(bot, discord_id)) 
            string += f"\n  {player.display_name} "
            if amount == 0:
                string += f" Lost"
            else:
                string += f" Won {amount}"
                player.modify_balance(amount)
                
        await du.send_persistant_message(ctx, string)
        await asyncio.sleep(5)
        await roulette_start(ctx, False)
                
