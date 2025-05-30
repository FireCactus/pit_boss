from typing import *
import asyncio
from discord import Message, User
from discord.ext import commands
from discord.ext.commands import Context, Bot

from player.Player import Player
from games.minigames.CoinToss import CoinTossDaily, CoinTossBet, HT
from games.minigames.Minigame import MinigameResult, GameResult
from bot_commands import discord_utilities as du



heads_reaction: str = "🇭"
tails_reaction: str = "🇹"

cointoss_reactions: list[str] = [
    heads_reaction,
    tails_reaction
]

start_game_countdown = 6


def setup(bot: Bot) -> None:

    @bot.command("cointoss")
    async def cointoss(ctx: Context) -> None:
        
        start_text: str = f"Coin toss game starting in {start_game_countdown} seconds!\nPlace your bets! (Chooses Tails If both selected)"
        await du.delete_message(ctx.message)
        bets: List[CoinTossBet] = []
        reaction_users: Dict[User, List[str]] = await du.send_standard_join_game_message(ctx, start_text, cointoss_reactions, start_game_countdown)
        for user, reactions in reaction_users.items():
            player: Player = Player(user)

            for reaction in reactions:
                if reaction not in cointoss_reactions:
                    continue
            
                pick: HT
                if reaction == heads_reaction:
                    pick = HT.HEADS
                        
                elif reaction == tails_reaction:
                    pick = HT.TAILS

                ct_bet: CoinTossBet = CoinTossBet(name=player.display_name, discord_id=player.discord_id, pick=pick)
                bets.append(ct_bet)
            
        game: CoinTossDaily = CoinTossDaily(_payout=20)
        game_results: List[MinigameResult] = game._determine_results(bets)
        await du.send_vanishing_message(ctx, f"It's {game._result.value}!",time_to_vanish=6)

        for result in game_results:
            player_final: Player = Player(await du.get_discord_user_from_id(bot, result.discord_id))
            
            if result.game_result == GameResult.WIN:
                player_final.modify_balance(result.payout)
                await du.send_persistant_message(ctx, f"{player_final.display_name} recieved {result.payout}!")

            else:
                await du.send_persistant_message(ctx, f"{player_final.display_name} lost coin toss and didnt get anything :(")