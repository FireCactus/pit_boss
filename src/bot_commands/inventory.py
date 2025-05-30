from discord import *
from discord.ext import commands
from discord.ext.commands import Context, Bot
from typing import *
import asyncio

from player.Item import Item
from player.Player import Player
from bot_commands import discord_utilities as du 

from games.scratch_off.TransportSearch import TransportSearch


def setup(bot: Bot) -> None:

    @bot.command("inv")
    async def get_inventory(ctx: Context, arg_1: Optional[str]) -> None:
        user: User = ctx.message.author
        await du.delete_message(ctx.message)
        
        if arg_1 == "all":
            pass # get everyones inv.
        else:
            player: Player = Player(user)
            items: list[Item] = player.get_all_items()
            
            string: str = ""
            if len(items)> 0:
                string += f"----------{player.display_name} inventory ----------\n"
                for i, item in enumerate(items):
                    string += f"[ {i+1} ] - {item.get_name()}\n"
            else:
                string += f"{player.display_name} your inventory is empty!"
            
            await du.send_vanishing_message(ctx, string)

    @bot.command("daj")
    async def give_item(ctx: Context, arg_1: Optional[str]) -> None:
        user: User = ctx.message.author
        await du.delete_message(ctx.message)
        player: Player = Player(user)
        item = TransportSearch()
        
        player.save_item_to_inventory(item)

