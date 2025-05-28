from discord import Message, User
from discord.ext import commands
from discord.ext.commands import Context, Bot
import asyncio
from typing import *

from games.Player import Player
from games.roulette.RouletteGame import RouletteGame, RouletteBet, RouletteOutcomes
from games.cardgames.blackjack.BlackjackGame import BlackjackGame, BlackjackPlayer
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
stand_reaction: str = "❌"
hit_reaction: str = "👆"
split_reaction: str = "↔️"
double_reaction: str = "🔥"
join_bj_game_reaction: str = "🃏"
unknown_card_emoji: str = "[?]"


start_game_countdown:int = 3 # how long to wait before starting a game

info_delete_after_seconds:int = 15

def setup(bot: Bot) -> None:

    @bot.command("bet")
    async def change_player_bet(ctx: Context, arg_1: str, arg_2: str) -> None:
        if arg_1 == "size":
            user: str = str(ctx.message.author)
            player: Player = Player(user)
            await ctx.message.delete()
           
            amount = int(arg_2)
            try:
                player.change_bet(amount)
                await ctx.send(f"Bet size for {player.name} changed to {amount}", delete_after=info_delete_after_seconds)
            except ValueError as e:
                await ctx.send(f"Bet size for {player.name} Unchanged!\nReason: {e}", delete_after=info_delete_after_seconds)


    @bot.command("all")
    async def change_bet_to_max(ctx: Context, arg_1: str) -> None:
        if arg_1 == "in":
            user: str = str(ctx.message.author)
            player: Player = Player(user)
            await ctx.message.delete()

            current_balance = player.get_balance()
            try:
                player.change_bet(current_balance)
                await ctx.send(f"Bet size for {player.name} changed to {current_balance}", delete_after=info_delete_after_seconds)
            except ValueError as e:
                await ctx.send(f"Bet size for {player.name} Unchanged!\nReason: {e}", delete_after=info_delete_after_seconds)


    @bot.command("roulette")
    async def roulette_start(ctx: Context, started_by_user: bool = True) -> None:

        # remove starting message
        if started_by_user:
            await ctx.message.delete()

        join_message: Message = await ctx.send(f"Spinning roulette table in {start_game_countdown} seconds, place your bets!")

        for reaction in roulette_reactions:
            await join_message.add_reaction(reaction)

        await asyncio.sleep(start_game_countdown)  # wait for everyone to place bets
        message: Message = await ctx.channel.fetch_message(join_message.id)  # refresh message to get all new reactions

        #create RouletteBet objects from user reactions
        roulette_bets: list[RouletteBet] = []
        for user_reaction in message.reactions:

            users: list[User] = [user async for user in user_reaction.users()]

            for user in users:
                if user == bot.user:
                    continue
                
                player = Player(str(user))
                pick: RouletteOutcomes
                if user_reaction.emoji == odd_reaction:
                    pick = RouletteOutcomes.ODD
                           
                elif user_reaction.emoji == even_reaction:
                    pick = RouletteOutcomes.EVEN
                    
                elif user_reaction.emoji == red_reaction:
                    pick = RouletteOutcomes.RED
                                   
                elif user_reaction.emoji == green_reaction:
                    pick = RouletteOutcomes.GREEN            
                
                elif user_reaction.emoji == black_reaction:
                    pick = RouletteOutcomes.BLACK
                
                bet: RouletteBet = RouletteBet(name=player.name, bet_amount=player.get_player_bet(), pick=pick)
                roulette_bets.append(bet)
                
        if started_by_user:
            await message.delete()  # remove starting message

        # Check if any player cannot afford the bet they made and make them pay 
        verified_bets: list[RouletteBet] = []
        for bet in roulette_bets:
            player = Player(bet.name)
            if player.get_balance() >= bet.bet_amount:
                verified_bets.append(bet)
                player.modify_balance(-bet.bet_amount)
            else:
                await ctx.send(f"Sorry {player.name}, You did not have enough money to bet {bet.bet_amount} on {bet.pick.name.lower().title()}. The bet was removed", delete_after=info_delete_after_seconds)

        if len(verified_bets) == 0:
            await ctx.send("Noone placed a bet :(", delete_after=info_delete_after_seconds)
            return None
            
        game: RouletteGame = RouletteGame()

        # print the bets
        string: str = "(Change your bet with !bet size [amount])\n"
        for bet in verified_bets:
            string += f"       -{bet.name} bet: {bet.bet_amount} on {bet.pick.value}\n"

        string += "------------------------------------------------------------"
        await ctx.send(string, delete_after=info_delete_after_seconds)

        # start game
        winners: dict[str,int] = await game.play(ctx, verified_bets)

        total_bet_by_user: dict[str, int] = {}
        for bet in verified_bets:
            if bet.name in total_bet_by_user.keys():
                total_bet_by_user[bet.name] += bet.bet_amount
            else:
                total_bet_by_user[bet.name] = bet.bet_amount

        #pay the winners
        winner_string: str = "---------- Roulette Results ----------\n"
        for player, amount in winners.items():
            winner_string += f"\n  {player} "
            if amount == 0:
                winner_string += f" lost {total_bet_by_user[player]}"
            else:
                winner_string += f" Won {amount - total_bet_by_user[player]}"
                player = Player(player)
                player.modify_balance(amount)
                
        await ctx.send(winner_string)
        await asyncio.sleep(5)
        await roulette_start(ctx, False)
                


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
        for username in await du.send_standard_join_game_message(ctx, start_text, join_bj_game_reaction, start_game_countdown):
            player = Player(str(username))
            balance: int = player.get_balance()
            bet: int = player.get_player_bet()

            if bet > balance:
                poor_text = f"Sorry {player.name} You have only {balance}, but you bet {bet}.\nChange your bet size using !bet size [amount]"
                await du.send_vanishing_message(ctx, poor_text)
            else:
                player.modify_balance(-bet)
                bj_player: BlackjackPlayer = BlackjackPlayer(player.name, bet)
                bj_players.append(bj_player)
        
        if len(bj_players) == 0:
            await du.send_vanishing_message(ctx, "Noone joined the table :(")
            return None

        game: BlackjackGame = BlackjackGame(bj_players)
        table_message: Message = await send_bj_table(ctx, game)
        #game loop
        for player in game.players:
            db_player:Player = Player(player.name) # initialize the player to check their balance
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

                    user_pick: Optional[str] = await du.send_message_and_wait_for_user_choice(ctx, text, valid_reactions, player.name)

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
        win_amounts: Dict[str, int] = game.calculate_win_amounts()
        win_string: str = "----------------------------------\n"
        for player, amount in win_amounts.items():
            db_player = Player(player)
            db_player.modify_balance(amount)

            if amount == 0:
                win_string +=  f"{player} Lost to the dealer\n"
            else:
                win_string += f"{player} Won: {amount}\n"

        win_string += "----------------------------------"
        await du.send_persistant_message(ctx, win_string)
        
        await asyncio.sleep(5)
        await start_blackjack_game(ctx, started_by_user=False)
    
            
