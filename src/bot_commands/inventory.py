from discord import *
from discord.ext import commands
from discord.ext.commands import Context, Bot
from typing import *
import asyncio

from database.PlayersDatabase import PlayersDatabase
from player.Item import Item
from player.Player import Player
from bot_commands import discord_utilities as du 
from player.CasualItem import CasualItemUsage, CasualItem


db = PlayersDatabase()

def setup(bot: Bot) -> None:

    @bot.command("inv")
    async def get_inventory(ctx: Context) -> None:
        user: User = ctx.message.author
        await du.delete_message(ctx.message)
        
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

    
    
    @bot.command("item")
    async def transfer_item(ctx: Context, arg_1: str, arg_2: str, arg_3: Optional[str]) -> None:
        if arg_1 == "give":

            from_player: Player = Player(ctx.message.author)
            await ctx.message.delete()

            to_user: User = ctx.message.mentions[0]
            try:
                item_in_inv: int = int(arg_3)

            except ValueError:
                await du.send_vanishing_message(ctx, f"'{arg_3}' is an invalid item index")
                return None

            #check if to player exists
            if db.check_if_player_exists(ctx.message.mentions[0].id) ==  False:
                await du.send_vanishing_message(ctx, f"Sorry, player with name {to_user} does not exist")
                return None            

            to_player: Player = Player(to_user)

            #check if from player has that item
            items: list[Item] = from_player.get_all_items()
            if len(items) < item_in_inv or item_in_inv < 1:
                await du.send_vanishing_message(ctx, f"Sorry {from_player.display_name} You have {len(items)} items, but you specified item no. {item_in_inv}")
                return None
        
            from_player.give_item_to_player(items[item_in_inv-1], to_player)
            await du.send_vanishing_message(ctx, f"Transferred {items[item_in_inv-1].get_name()} from {from_player.display_name} to {to_player.display_name}")

        if arg_1 == "use":
            
            player: Player = Player(ctx.message.author)
            await ctx.message.delete()

            item_in_inv: int = int(arg_2)
            items: list[Item] = player.get_all_items()
            if len(items) < item_in_inv or item_in_inv < 1:
                await du.send_vanishing_message(ctx, f"Sorry {from_player.display_name} You have {len(items)} items, but you specified item no. {item_in_inv}")
                return None
            
            item = items[item_in_inv-1]
            await du.send_persistant_message(ctx, f"{player.display_name} used {item.get_name()}!")

            if issubclass(type(item), CasualItem):
                message: str = item.use().returned_string
                await du.send_persistant_message(ctx, message)
                
                #pay the user and remove the item 
                player.modify_balance(item.get_win_amount())
                
                if item.get_uses_left() == 0:
                    player.delete_item_from_inventory(item)

            
            

            






