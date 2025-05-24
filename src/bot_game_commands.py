from discord import Message, User
from discord.ext import commands
from discord.ext.commands import Context, Bot
import asyncio

from games.Player import Player
from games.roulette.RouletteGame import RouletteGame, RouletteBet, RouletteOutcomes
from games.cardgames.blackjack.BlackjackGame import BlackjackGame, BlackjackPlayer

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

join_bj_game_reaction: str = "🃏"

start_game_countdown:int = 6 # how long to wait before starting a game

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
    async def roulette_start(ctx: Context) -> None:

        # remove starting message
        user: str = str(ctx.message.author)
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

        game: RouletteGame = RouletteGame()

        # print the bets
        string: str = "(Change your bet with !bet size [amount])\n"
        for bet in verified_bets:
            string += f"       -{bet.name} bet: {bet.bet_amount} on {bet.pick.name.lower().title()}\n"

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
        roulette_start(ctx)
                


    @bot.command("blackjack")
    async def start_blackjack_game(ctx: Context) -> None:
        
        # remove starting message
        user: str = str(ctx.message.author)
        await ctx.message.delete()

        join_message: Message = await ctx.send(f"Starting blackjack game in {start_game_countdown} seconds!\nClick the emoji to join")
        await join_message.add_reaction(join_bj_game_reaction)

        await asyncio.sleep(start_game_countdown)  # wait for everyone to place bets
        message: Message = await ctx.channel.fetch_message(join_message.id)  # refresh message to get all new reactions

        #create BlackjackPlayer objects from players
        bj_players: list[BlackjackPlayer] = []
        for user_reaction in message.reactions:
            users: list[User] = [user async for user in user_reaction.users()]

            for user in users:
                if user == bot.user:
                    continue
        
                player = Player(str(user))
                balance: int = player.get_balance()
                bet: int = player.get_player_bet()
                if bet > balance:
                    await ctx.send(f"Sorry {player.name} You have only {balance}, but you bet {bet}.\nChange your bet size using !bet size [amount]", delete_after=info_delete_after_seconds)
                else:
                    player.modify_balance(-bet)
                    bj_player: BlackjackPlayer = BlackjackPlayer(player.name, bet, balance)
                    bj_players.append(bj_player)
        
        if len(bj_players) == 0:
            await ctx.send("Noone joined the table :(", delete_after=info_delete_after_seconds)
            return None

        await message.delete()  # remove starting message

        #play game
        game: BlackjackGame = BlackjackGame(bj_players)
        winners: dict[str,int] = await game.start(ctx)

        #pay the winners
        winner_string: str = "---------- BlackJack Results ----------\n"
        for user, amount in winners.items():
            player = Player(user)
            bet = [bj_player.initial_bet for bj_player in bj_players if bj_player.name == player.name][0]
            winner_string += f"\n  {player.name} "
            if amount == bet:
                winner_string += f" broke even!"
                player.modify_balance(bet)
            elif amount == 0:
                winner_string += f"lost their bet ({bet})"

            elif amount < 0:
                winner_string += f" lost {-amount}"
                player.modify_balance(amount)
            else:
                winner_string += f" Won {amount}"
                player.modify_balance(amount)
        winner_string +=  "\n-----------------------------------------"
                
        await ctx.send(winner_string)
        await asyncio.sleep(5)
        roulette_start(ctx)