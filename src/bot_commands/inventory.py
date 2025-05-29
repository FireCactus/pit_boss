from discord import *
from discord.ext import commands
from discord.ext.commands import Context, Bot
from typing import *
import asyncio


from player.Player import Player
from bot_commands import discord_utilities as du 



def setup(bot: Bot) -> None:

    @bot.command("inventory")
    async def get_inventory(ctx: Context, arg_1: Optional[str]) -> None:
        user: str = str(ctx.message.author)
        await du.delete_message(ctx.message)
        
        if arg_1 == "all":
            pass # get everyones inv.
        else:
            player: Player = Player(user)
            # get players inv