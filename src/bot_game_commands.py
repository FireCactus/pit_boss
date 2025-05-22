from discord.ext import commands
from games import game_player as g_player

from games.cardgames.blackjack import blackjack as bj
from games.roulette import roulette as rlt

odd_reaction = "1️⃣"
even_reaction = "2️⃣"
black_reaction = "⬛"
red_reaction = "🟥"
green_reaction = "🟩"
roulette_reactions = [
    green_reaction,
    black_reaction,
    red_reaction,
    even_reaction,
    odd_reaction,
]

join_bj_game_reaction = "🃏"

start_game_in = 6

starting_money = 500
min_bet = 25
max_bet = 1000
daily_reward = 75

bet_size_table = {}


async def init_bet_size_table(ctx, players):
    for player in players:
        # check if player has a bet, if not set to minimal
        if player.name not in bet_size_table.keys():
            bet_size_table[player.name] = min_bet
            # check fif playr can afford the bet hes trying to make (more than 1 bet )

        # if a player entered a game with a bet that is bigger than their balance, change their bet to minimal
        elif player.money < bet_size_table[player.name]:
            await ctx.send(
                f"{player.name}, Your bet was set at {bet_size_table[player.name]} but you only have {player.money}\nSetting your bet at the minimum ({min_bet})",
                delete_after=info_delete_after_seconds,
            )
            bet_size_table[player.name] = min_bet


def setup(bot):
    @bot.command("bet")
    async def change_player_bet(ctx, arg_1, arg_2):
        if arg_1 == "size":
            user = str(ctx.message.author)
            await ctx.message.delete()

            init_player(user)
            player = g_player.load_player_from_file(user)

            try:
                arg_2 = int(arg_2)

                assert arg_2 >= min_bet
                assert arg_2 <= max_bet
                assert arg_2 <= player.money

                bet_size_table[user] = arg_2
                await ctx.send(
                    f"Bet size for {user} changed to {arg_2}",
                    delete_after=info_delete_after_seconds,
                )
            except Exception as e:
                if arg_2 > player.money:
                    await ctx.send(
                        f"You do not have enough money to bet {arg_2}, You only have {player.money}",
                        delete_after=info_delete_after_seconds,
                    )
                else:
                    await ctx.send(
                        f"invalid bet size amount!\nBet has to be in between {min_bet}-{max_bet}",
                        delete_after=info_delete_after_seconds,
                    )
                print(e)

    @bot.command("all")
    async def change_bet_to_max(
        ctx,
        arg_1,
    ):
        if arg_1 == "in":
            user = str(ctx.message.author)

            init_player(user)
            player = g_player.load_player_from_file(user)

            await ctx.message.delete()

            if player.money < min_bet:
                await ctx.send(
                    f"Sorry {player.name}, You only have {player.money} and {min_bet} is the minimum bet",
                    delete_after=info_delete_after_seconds,
                )
                return None

            if player.money >= max_bet:
                bet = max_bet
            else:
                bet = player.money

            bet_size_table[user] = bet
            await ctx.send(
                f"Bet size for {user} changed to {bet}",
                delete_after=info_delete_after_seconds,
            )

    @bot.command("roulette")
    async def roulette_start(ctx):

        # remove starting message
        user = str(ctx.message.author)
        init_player(user)
        await ctx.message.delete()

        message = await ctx.send(
            f"Spinning roulette table in {start_game_in} seconds, place your bets!"
        )
        for reaction in roulette_reactions:
            await message.add_reaction(reaction)

        await asyncio.sleep(start_game_in)  # wait for everyone to place bets
        message = await ctx.channel.fetch_message(
            message.id
        )  # refresh message to get all new reactions

        roulette_players = []
        for reaction in message.reactions:
            users = [user async for user in reaction.users()]

            for user in users:
                if user == bot.user:
                    continue

                player = g_player.load_player_from_file(str(user))

                if reaction.emoji == odd_reaction:
                    player.roulette_pick_number = "odd"
                    player.roulette_pick_color = None

                elif reaction.emoji == even_reaction:
                    player.roulette_pick_number = "even"
                    player.roulette_pick_color = None

                elif reaction.emoji in [black_reaction, red_reaction, green_reaction]:
                    player.roulette_pick_color = reaction.emoji
                    player.roulette_pick_number = None

                roulette_players.append(player)

        await message.delete()  # remove starting message

        # init bet table
        await init_bet_size_table(ctx, roulette_players)
        bet_size_table_game = bet_size_table.copy()

        game = rlt.RouletteGame()
        # add players to game
        for player in roulette_players:
            if player.money >= min_bet:
                game.add_player_to_game(player)

        if len(roulette_players) < 1:
            await ctx.send(
                "noone placed a bet", delete_after_seconds=info_delete_after_seconds
            )
            return None

        # print the bets
        string = "(Change your bet with !bet size [amount])\n"
        for player in roulette_players:
            if player.roulette_pick_color != None:
                string += f"       -{player.name} bet: {bet_size_table[player.name]} on {player.roulette_pick_color}\n"
            if player.roulette_pick_number != None:
                string += f"       -{player.name} bet: {bet_size_table[player.name]} on {player.roulette_pick_number}\n"

        string += "------------------------------------------------------------"
        await ctx.send(string, delete_after=delete_after_seconds)

        # start game
        await game.start_game_discord(ctx, bet_size_table_game)

    @bot.command("blackjack")
    async def start_blackjack_game(ctx):
        try:
            await ctx.message.delete()  # delete users start message
        except:
            pass

        message = await ctx.send(
            f"Starting blackjack game!\nClick the reaction to join the table! (starting in {start_game_in} seconds!)",
            delete_after=start_game_in + 2,
        )
        await message.add_reaction(join_bj_game_reaction)

        await asyncio.sleep(start_game_in)
        message = await ctx.channel.fetch_message(message.id)

        users_playing_bj = []
        users = [user async for user in message.reactions[0].users()]
        for user in users:
            if user == bot.user:
                continue
            users_playing_bj.append(str(user))

        if len(users_playing_bj) < 1:
            await ctx.send(
                "Noone joined the table! :( ", delete_after=info_delete_after_seconds
            )
            return None

        # initialize bj users
        bj_players = []

        for user in users_playing_bj:
            init_player(user)
            player = g_player.load_player_from_file(user)

            if player.money >= min_bet:
                bj_players.append(player)
            else:
                await ctx.send(
                    f"Sorry {user}, You have only {player.money}!\n minimal bet is {min_bet}",
                    delete_after=info_delete_after_seconds,
                )

        if len(users_playing_bj) < 1:
            await ctx.send(
                "No players at the table! ", delete_after=info_delete_after_seconds
            )
            return None

        # initialize bet table
        await init_bet_size_table(ctx, bj_players)

        game = bj.BlackjackGame()

        for player in bj_players:
            game.add_player_to_game(player)

        string = "(Change your bets with !bet size [amount])\n"

        for player in bj_players:
            string += f"       -{player.name} bet: {bet_size_table[player.name]}\n"
        string += "------------------------------------------------------------"

        await ctx.send(string, delete_after=delete_after_seconds)
        bet_size_table_game = bet_size_table.copy()
        await game.start_game_discord(ctx, bet_size_table_game)

        await asyncio.sleep(4)
        await start_blackjack_game(ctx)  # start game again!
