from discord import Message, User
from discord.ext import commands
from discord.ext.commands import Context, Bot
from typing import *
import asyncio
import os
import time
import random

from player.Player import Player
from games.pvp.ConnectFour import ConnectFourBoard, ConnectFourToken, ConnectFourColor
from bot_commands import discord_utilities as du 
from database.PlayersDatabase import PlayersDatabase

db = PlayersDatabase()

column_emoji_dict: Dict[int,str]={
    1 : "1️⃣",
    2 : "2️⃣",
    3 : "3️⃣",
    4 : "4️⃣",
    5 : "5️⃣",
    6 : "6️⃣",
    7 : "7️⃣"
}
#reversed dict form getting the column number back from the emoji
emoji_column_dict = {v: k for k, v in column_emoji_dict.items()}

accept_duel_emoji: str = "✅"
refuse_duel_emoji: str = "❌"

challenge_games: Dict[str,str] = {
    "4️⃣": "Connect 4"
}

player_accept_challenge_timeout=90
player_make_move_timeout = 60

def setup(bot: Bot) -> None:

    @bot.command("challenge")
    async def challenge_player_to_duel(ctx: Context, arg_1: str, arg_2:str) -> None:
        
        challenging_player: Player = Player(ctx.message.author)
        challenged_player: Player = Player(ctx.message.mentions[0])

        await du.delete_message(ctx.message)

        if db.check_if_player_exists(ctx.message.mentions[0].id) ==  False:
            await du.send_vanishing_message(ctx, f"Sorry, player with name {challenged_player.display_name} does not exist")
            return None  

        amount: int = int(arg_2)
        if amount <= 0:
            await du.send_vanishing_message(ctx,f"To challenge a player to a game you need to bet at least 1")
            return None
        
        balance: int = challenging_player.get_balance()
        if balance < amount:
            await du.send_vanishing_message(ctx,f"Sorry, you only have {balance} but you wagered {amount}")
            return None 

        
        balance = challenged_player.get_balance()
        if balance < amount:
            await du.send_vanishing_message(ctx,f"Sorry, {challenged_player.display_name} only has {balance} and you wagered {amount}")
            return None

        
        string : str = f"{challenging_player.display_name} what game do you wish to challenge {challenged_player.display_name} at?\n"
        for emoji, game in challenge_games.items():
            string += f"-{game} -> {emoji}"

        game_choice: Optional[str] = await du.send_message_and_wait_for_user_choice(ctx,
            string,
            challenge_games.keys(),
            challenging_player.discord_user
        )
        
        if game_choice == None:
            du.send_vanishing_message(ctx, f"Failed to select the challenge game in time.")
            return None
        
            
        string = f"{challenged_player.display_name}!\n"
        string += f"{challenging_player.display_name} has challenged you to a match of {challenge_games[game_choice]} and wagered {amount} that they will win!\n"
        string += f"If you accept this challenge click the {accept_duel_emoji} reaction below\n"
        string += f"If you wish to refuse the duel, click the {refuse_duel_emoji} reaction"

        accept_choice: Optional[str] = await du.send_message_and_wait_for_user_choice(ctx,
            string,
            [accept_duel_emoji, refuse_duel_emoji],
            challenged_player.discord_user,
            player_accept_challenge_timeout
        )

        if accept_choice != accept_duel_emoji:
            await du.send_vanishing_message(ctx, f"{challenged_player.display_name} has refused the duel")
            return None
        
        if challenge_games[game_choice] == "Connect 4":
            await du.send_persistant_message(ctx, f"{challenged_player.display_name} has accepted {challenging_player.display_name}'s challenge at Connect 4!\n{challenging_player.display_name} you are playing as 🔴\n{challenged_player.display_name} you are playing as 🟡")
            await play_connect_four(ctx, challenging_player, challenged_player, amount)
        


    async def play_connect_four(context: Context, challenging_player: Player, challenged_player: Player, amount: int):
        '''
        The player that started the challenge goes first (red tokens)
        the other player goes second and plays with yellow tokens
        '''
        
        board: ConnectFourBoard = ConnectFourBoard()
    
        #send initial table message
        board_message: Message = await du.send_persistant_message(context, board.get_fields_as_emoji_string())

        while True:
            #Red player turn
            string: str = f"{challenging_player.display_name} It's your turn, select a row to drop in your piece in"
            vacant_columns: list[int] = board.get_vacant_columns()
            if len(vacant_columns) == 0:
                # game has finished in a draw
                break

            token: ConnectFourToken = ConnectFourToken(ConnectFourColor.RED)
            vacant_columns_emojis: list[str] = [column_emoji_dict[col] for col in vacant_columns]
            row_choice: Optional[str] = await du.send_message_and_wait_for_user_choice(context, string, vacant_columns_emojis, challenging_player.discord_user, player_make_move_timeout)
            
            if row_choice == None:
                board.insert_token_into_column(random.choice(vacant_columns), token)
            else:
                board.insert_token_into_column(emoji_column_dict[row_choice], token)
            
            board_message = await du.edit_message(board_message, board.get_fields_as_emoji_string())
            
            if board.check_for_wins() != None:
                break

            #Yellow player turn
            string: str = f"{challenged_player.display_name} It's your turn, select a row to drop in your piece in"
            vacant_columns: list[int] = board.get_vacant_columns()
            if len(vacant_columns) == 0:
                # game has finished in a draw
                break

            token: ConnectFourToken = ConnectFourToken(ConnectFourColor.YELLOW)
            vacant_columns_emojis: list[str] = [column_emoji_dict[col] for col in vacant_columns]
            row_choice: Optional[str] = await du.send_message_and_wait_for_user_choice(context, string, vacant_columns_emojis, challenged_player.discord_user, player_make_move_timeout)
            
            if row_choice == None:
                board.insert_token_into_column(random.choice(vacant_columns), token)
            else:
                board.insert_token_into_column(emoji_column_dict[row_choice], token)
            
            board_message = await du.edit_message(board_message, board.get_fields_as_emoji_string())
    
        ### game concluded

        winner: Optional[ConnectFourColor] = board.check_for_wins()

        if winner == None:
            await du.send_persistant_message(context, f"{challenging_player.display_name} and {challenged_player.display_name} met their match at Connect 4!\n No one Won or lost")

        if winner == ConnectFourColor.RED:
            await du.send_persistant_message(context, f"{challenging_player.display_name} Won against {challenged_player.display_name} at Connect 4!\n Transferring {amount} to {challenging_player.display_name} from {challenged_player.display_name}'s account")
            challenging_player.modify_balance(amount)
            challenged_player.modify_balance(-amount)
        
        else:
            await du.send_persistant_message(context, f"{challenged_player.display_name} Won against {challenging_player.display_name} at Connect 4!\n Transferring {amount} to {challenged_player.display_name} from {challenging_player.display_name}'s account")
            challenged_player.modify_balance(amount)
            challenging_player.modify_balance(-amount)