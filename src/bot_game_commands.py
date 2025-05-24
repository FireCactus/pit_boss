from discord import Message, User
from discord.ext import commands
from discord.ext.commands import Context

from games import Player
from games.cardgames.blackjack import blackjack as bj
from games.roulette.RouletteGame import RouletteGame, RouletteBet

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

def setup(bot):

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
    async def change_bet_to_max(ctx: Context, arg_1: str):
        if arg_1 == "in":
            user: str = str(ctx.message.author)
            player: Player = Player(user)
            await ctx.message.delete()

            current_balance = player.get_balance()
            try:
                player.change_bet(current_balance)
                await ctx.send(f"Bet size for {player.name} changed to {amount}", delete_after=info_delete_after_seconds)
            except ValueError as e:
                await ctx.send(f"Bet size for {player.name} Unchanged!\nReason: {e}", delete_after=info_delete_after_seconds)


    @bot.command("roulette")
    async def roulette_start(ctx: Context):

        # remove starting message
        user: str = str(ctx.message.author)
        await ctx.message.delete()

        message: Message = await ctx.send(f"Spinning roulette table in {start_game_countdown} seconds, place your bets!")

        for reaction in roulette_reactions:
            await message.add_reaction(reaction)

        await asyncio.sleep(start_game_countdown)  # wait for everyone to place bets
        message = await ctx.channel.fetch_message(
            message.id
        )  # refresh message to get all new reactions

        #create RouletteBet objects from user reactions
        roulette_bets: list[RouletteBet] = []
        for reaction in message.reactions:
            users: list[User] = [user async for user in reaction.users()]

            for user in users:
                if user == bot.user:
                    continue
                
                player = Player(str(user))

                if reaction.emoji == odd_reaction:
                    bet: RouletteBet = RouletteBet(name=player.name, bet_amount=player.get_player_bet, pick="Odd")
                    roulette_bets.append(bet)
                
                elif reaction.emoji == even_reaction:
                    bet: RouletteBet = RouletteBet(name=player.name, bet_amount=player.get_player_bet, pick="Even")
                    roulette_bets.append(bet)
                
                elif reaction.emoji == red_reaction:
                    bet: RouletteBet = RouletteBet(name=player.name, bet_amount=player.get_player_bet, pick="Red")
                    roulette_bets.append(bet)
                
                elif reaction.emoji == green_reaction:
                    bet: RouletteBet = RouletteBet(name=player.name, bet_amount=player.get_player_bet, pick="Green")
                    roulette_bets.append(bet)
                
                elif reaction.emoji == black_reaction:
                    bet: RouletteBet = RouletteBet(name=player.name, bet_amount=player.get_player_bet, pick="Black")
                    roulette_bets.append(bet)
                

        await message.delete()  # remove starting message

        # Check if any player cannot afford the bet they made and make them pay 
        verified_bets: list[RouletteBet] = []
        for bet in roulette_bets:
            player: Player = Player(bet.name)
            if player.get_balance() >= bet.bet_amount:
                verified_bets.append(bet)
                player.modify_balance(-bet.bet_amount)
            else:
                await ctx.send(f"Sorry {player.name}, You did not have enough money to bet {bet.bet_amount} on {bet.pick}. The bet was removed", delete_after=info_delete_after_seconds)

        if len(verified_bets) == 0:
            await ctx.send("Noone placed a bet :(", delete_after=info_delete_after_seconds)

        game: RouletteGame = RouletteGame()

        # print the bets
        string: str = "(Change your bet with !bet size [amount])\n"
        for bet in verified_bets:
            string += f"       -{bet.name} bet: {bet.bet_amount} on {bet.pick}\n"

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
        string: str = "---------- Roulette Results ----------\n"
        for player, amount in winners.items():
            string += f"  {player} "
            if amount == 0:
                string += f" lost {total_bet_by_user[player]}"
            else:
                string += f" Won {amount - total_bet_by_user[player]}"
                player: Player = Player(bet.user)
                player.modify_balance(amount)
                
        await ctx.send(string)
                


    @bot.command("blackjack")
    async def start_blackjack_game(ctx: Context):
        pass