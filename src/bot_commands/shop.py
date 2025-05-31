from discord import *
from discord.ext import commands
from discord.ext.commands import Context, Bot
from typing import *
import asyncio

from player.Item import Item
from player.Player import Player
from player.Shop import Shop
from bot_commands import discord_utilities as du 

from games.scratch_off.TransportSearch import TransportSearch
from games.scratch_off.DiamondRush import DiamondRush
from games.scratch_off.EmojiLines import EmojiLines
from games.scratch_off.SuperPayout import SuperPayout

shop_message_linger: int = 30


def setup(bot: Bot) -> None:
    
    @bot.command("shop")
    async def get_inventory(ctx: Context, arg_1: Optional[str], arg_2: Optional[str]) -> None:
        user: User = ctx.message.author

        if arg_1 == None:
            await du.delete_message(ctx.message)
            shop: Shop = Shop()
            shop_items: list[Item] = shop.get_items_in_stock()

            string: str = "-------------------- Shop --------------------\n"
            string += "Buy using !shop buy [number]\n"
            string += "Try using !shop buy 1,4,5 to buy multiple at a time\n\n"

            if len(shop_items) == 0:
                string += "The Store is empty!\n but don't worry, it restocks at midnight"

            for i, item in enumerate(shop_items):
                string += f"  [ {i+1} ] - {item.get_representation_emoji()}{item.get_name()} ({item.get_price()})\n"
                string += f"        {item.get_description()}\n\n"
            
            await du.send_vanishing_message(ctx, string, shop_message_linger)
        
        
        elif arg_1 == "buy":
            await du.delete_message(ctx.message)

            shop: Shop = Shop()
            shop_items: list[Item] = shop.get_items_in_stock()
            
            # get user choices and cast them to to int
            item_choices: list[int] = [int(choice) for choice in arg_2.split(",")]
            
            #check if all items the user is requesting actually exist
            purchases: list[Item] = []
            purchase_cost: int = 0
            for choice in item_choices:                
                if choice > len(shop_items) or choice <=0:
                    await du.send_vanishing_message(ctx, f"There is no item in the shop with the number {arg_2}")
                    return None

                item: Item = shop_items[choice-1]
                purchases.append(item)
                purchase_cost += item.get_price()


            player: Player = Player(user)
            #check if can afford such a purchase
            player_balance: int = player.get_balance()

            if player_balance < purchase_cost:
                await du.send_vanishing_message(ctx, f"Sorry {player.display_name} You only have {player_balance} while this purchase would cost {purchase_cost}")
                return None

            for item in purchases:
                player.give_item_to_player(item, player)
             
            #remove money from player
            player.modify_balance(-purchase_cost)

            #let the user know what he bought:
            string: str = f"{player.display_name} bought the items:\n"
            for item in purchases:
                string += f"- {item.get_name()}\n"

            await du.send_vanishing_message(ctx, string)

        elif arg_1 == "restock_please":
            shop: Shop = Shop()
            shop.restock()