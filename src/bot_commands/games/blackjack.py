from discord import Message, User
from discord.ext import commands
from discord.ext.commands import Context, Bot
from typing import *
import asyncio

from player.Player import Player
from games.cardgames.blackjack.BlackjackGame import BlackjackGame, BlackjackPlayer
from bot_commands import discord_utilities as du 


stand_reaction: str = "❌"
hit_reaction: str = "👆"
split_reaction: str = "↔️"
double_reaction: str = "🔥"
join_bj_game_reaction: str = "🃏"
unknown_card_emoji: str = "[?]"


start_game_countdown:int = 6 # how long to wait before starting a game

def setup(bot: Bot) -> None:

    @bot.command("blackjack")
    async def start_blackjack_game(ctx: Context, started_by_user: bool = True) -> None:

        async def send_bj_table(ctx: Context, game: BlackjackGame, edit_message: Optional[Message]=None) -> Message:
            string: str = "----------------------------------------\n"
            string += f"Dealer: ({game.dealer_hand_value})\n"
            for card in game.dealer_cards:
                if card.face_down == False:
                    value = card.get_value()
                    color = card.get_color_emoji()

                    string += f"{value}{color}  "
                else:
                    string += f"{unknown_card_emoji}\n"

            string += "\n"
            for player in game.players:
                string += f"{player.name}:\n"
                for hand in player.hands:
                    string += f"bet: {hand.bet}:  "
                    for card in hand.cards:
                        if card.face_down == False:
                            value = card.get_value()
                            color = card.get_color_emoji()
                            string += f"{value}{color}  "
                        else:
                            string += f"{unknown_card_emoji}  "

                    string += f"-  ({hand.value})\n"

            message: Message
            if edit_message == None:
                message = await du.send_persistant_message(ctx, string)
            else:
                message = await du.edit_message(edit_message, string)
            
            return message
        

        # Delete the !blackjack message used to start the game
        if started_by_user:
            await du.delete_message(ctx.message)
        start_text: str = f"Starting blackjack game in {start_game_countdown} seconds!\nClick the emoji to join"
        
        bj_players: list[BlackjackPlayer] = []
        for user in await du.send_standard_join_game_message(ctx, start_text, join_bj_game_reaction, start_game_countdown):
            player = Player(user)
            balance: int = player.get_balance()
            bet: int = player.get_player_bet()

            if bet > balance:
                poor_text = f"Sorry {player.display_name} You have only {balance}, but you bet {bet}.\nChange your bet size using !bet size [amount]"
                await du.send_vanishing_message(ctx, poor_text)
            else:
                player.modify_balance(-bet)
                bj_player: BlackjackPlayer = BlackjackPlayer(player.display_name, player.discord_id, bet)
                bj_players.append(bj_player)
        
        if len(bj_players) == 0:
            await du.send_vanishing_message(ctx, "Noone joined the table :(")
            return None

        game: BlackjackGame = BlackjackGame(bj_players)
        table_message: Message = await send_bj_table(ctx, game)
        #game loop
        for player in game.players:
            dc_user: User = await du.get_discord_user_from_id(bot, player.discord_id)
            db_player:Player = Player(dc_user) # initialize the player to check their balance
            for hand in player.hands:
                while hand.in_play:
                    table_message = await send_bj_table(ctx, game, table_message)
                    
                    balance= db_player.get_balance()
                    valid_reactions: list[str] = [stand_reaction, hit_reaction]
                    if balance >= hand.bet: # if the player can afford a split or double, let them
                        if hand.is_doubleable():
                            valid_reactions.append(double_reaction)
                        if hand.is_splittable():
                            valid_reactions.append(split_reaction)

                    text: str = (
                        f"{player.name} it's your turn, what do you want to do?\n"
                        f"Current hand total is {hand.value}\n"
                        f"You bet {hand.bet} on this hand\n"
                        f"Your current balance is {balance}"
                        )

                    user_pick: Optional[str] = await du.send_message_and_wait_for_user_choice(ctx, text, valid_reactions, dc_user)

                    if user_pick == None:
                        user_pick = stand_reaction
                    
                    if user_pick == stand_reaction:
                        game.stand_player(player)
                    
                    elif user_pick == hit_reaction:
                        game.hit_player(player)

                    elif user_pick == double_reaction:
                        db_player.modify_balance(-hand.bet)
                        game.double_player(player)
                        
                    elif user_pick == split_reaction:
                        db_player.modify_balance(-hand.bet)
                        game.split_player(player)
        
        # The player turns are over, play the dealer 
        game.reveal_dealer_card()
        table_message = await send_bj_table(ctx, game, table_message)
        while game.dealer_hand_value < game._dealer_draws_to:
            await asyncio.sleep(1) # wait for 1 second inbetween card draws
            table_message = await send_bj_table(ctx, game, table_message)

            game.draw_dealer_card()
        
        await asyncio.sleep(1)
        #Reveal all players cards if any of them are down
        for player in game.players:
            game.reveal_player_cards(player)
        table_message = await send_bj_table(ctx, game, table_message)

        #game has concluded, get win amounts!
        win_amounts: Dict[User, int] = game.calculate_win_amounts()
        win_string: str = "----------------------------------\n"
        for player, amount in win_amounts.items():
            db_player = Player(await du.get_discord_user_from_id(bot, player.discord_id))
            db_player.modify_balance(amount)

            if amount == 0:
                win_string +=  f"{player.name} Lost to the dealer\n"
            else:
                win_string += f"{player.name} Won: {amount}\n"

        win_string += "----------------------------------"
        await du.send_persistant_message(ctx, win_string)
        
        await asyncio.sleep(5)
        await start_blackjack_game(ctx, started_by_user=False)
    
            
