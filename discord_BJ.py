import discord
from discord.ext import commands
from env import token
import asyncio

import blackjack as bj

intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
intents.messages = True
intents.guilds = True

start_game_in = 6

join_game_reaction = "🃏"
starting_money=500
min_bet = 25
max_bet = 1000
daily_reward = 75


bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
bet_size_table = {}
delete_after_seconds = 60
info_delete_after_seconds = 15


def init_player(user):
    try:
        player = bj.load_player_from_file(user)
    except:
        player = bj.BlackjackPlayer(user, starting_money)
        bj.save_player_to_file(player)

@bot.command("help")
async def help(ctx):
    await ctx.message.delete()

    string = f"!daily -> Gives you a daily reward of {daily_reward} (renewable at midnight)\n"
    string += f"!balance -> Returns your current balance\n"
    string += f"!balance all -> Returns the balances of all players\n"
    string += f"!blackjack -> Starts a blackjack game\n"
    string += f"!bet size [amount] -> Changes your bet size to the provided amount\n"
    string += f"!give [player name] [amount] -> Transfers an amount of money from your account to the provided users\n"
    string += f"!all in -> Changes your bet size to the maximum allowed\n"

    await ctx.send(string, delete_after=info_delete_after_seconds*2)


@bot.command("all")
async def change_bet_to_max(ctx, arg_1, ):
    if arg_1 == "in":
        user = str(ctx.message.author)

        init_player(user)
        player = bj.load_player_from_file(user)    

        await ctx.message.delete()

        if player.money < min_bet:
            await ctx.send(f"Sorry {player.name}, You only have {player.money} and {min_bet} is the minimum bet",delete_after=info_delete_after_seconds)
            return None

        if player.money >= max_bet:
            bet = max_bet
        else:
            bet = player.money

        bet_size_table[user] = bet
        await ctx.send(f"Bet size for {user} changed to {bet}",delete_after=info_delete_after_seconds)

@bot.command("daily")
async def change_bet_to_max(ctx):
    user = str(ctx.message.author)

    init_player(user)
    player = bj.load_player_from_file(user)    

    await ctx.message.delete()

    if player.received_daily:
        await ctx.send(f"Sorry {player.name}, You already received your daily reward!",delete_after=info_delete_after_seconds)
        return None
    
    player.received_daily = True
    player.money += daily_reward

    bj.save_player_to_file(player)
    await ctx.send(f"{player.name} received their daily reward! {daily_reward} added to balance",delete_after=info_delete_after_seconds)



@bot.command("bet")
async def change_player_bet(ctx, arg_1, arg_2):
    if arg_1 == "size":
        user = str(ctx.message.author)
        await ctx.message.delete()

        init_player(user)
        player = bj.load_player_from_file(user)    
    
        try:
            arg_2 = int(arg_2)
            
            assert arg_2 >= min_bet
            assert arg_2 <= max_bet
            assert arg_2 <= player.money

            bet_size_table[user] = arg_2
            await ctx.send(f"Bet size for {user} changed to {arg_2}",delete_after=info_delete_after_seconds)
        except Exception as e:
            if arg_2 > player.money:
                await ctx.send(f"You do not have enough money to bet {arg_2}, You only have {player.money}",delete_after=info_delete_after_seconds)
            else:
                await ctx.send(f"invalid bet size amount!\nBet has to be in between {min_bet}-{max_bet}",delete_after=info_delete_after_seconds)
            print(e)

@bot.command("give")
async def transfer_money(ctx, arg_1, arg_2):
    #init from user
    user = str(ctx.message.author)
    await ctx.message.delete()
    init_player(user)

    
    from_user =  bj.load_player_from_file(user)
    to_user = arg_1
    try:
        amount = int(arg_2)
    except:
        await ctx.send(f"{arg_2} is an invalid amount",delete_after=info_delete_after_seconds)
    
    player_names = []
    for player in bj.load_all_players():
        player_names.append(player.name)
    
    if to_user not in player_names:
        await ctx.send(f"No such User as {to_user}",delete_after=info_delete_after_seconds)
    else:
        to_user = bj.load_player_from_file(to_user)
    
    if to_user.name == from_user.name:
        await ctx.send(f"You can't send money to yourself",delete_after=info_delete_after_seconds)
        return

    if amount > from_user.money:
        await ctx.send(f"Insufficient money! You only have {from_user.money}",delete_after=info_delete_after_seconds)
    elif amount < 0:
        with open('wesker-no-wesker-no-no.gif', 'rb') as f:
            gif = discord.File(f)
            await ctx.send(file=gif)
    else:
        from_user.money -= amount
        to_user.money += amount
        await ctx.send(f"Transferred {amount} from {from_user.name} to {to_user.name}",delete_after=info_delete_after_seconds)

        bj.save_player_to_file(from_user)
        bj.save_player_to_file(to_user)

        

@bot.command("balance")
async def get_user_balance(ctx, arg_1=None):
    user = str(ctx.message.author)
    await ctx.message.delete()
    try:
        player = bj.load_player_from_file(user)
    except:
        player = bj.BlackjackPlayer(user, starting_money)
        bj.save_player_to_file(player)
    
    if arg_1 == "all":
        string = "---- All players money ----\n"
        for player in bj.load_all_players():
            string += f"{player.name}   {player.money}\n--------------------\n"
        await ctx.send(string,delete_after=info_delete_after_seconds)
    else:
        await ctx.send(f"{user} balance: {player.money}",delete_after=info_delete_after_seconds)



@bot.command("blackjack")
async def start_blackjack_game(ctx):
    try:
        await ctx.message.delete() # delete users start message
    except:
        pass

    message = await ctx.send(f"Starting blackjack game!\nClick the reaction to join the table! (starting in {start_game_in} seconds!)",delete_after=start_game_in+2)
    await message.add_reaction(join_game_reaction)

    await asyncio.sleep(start_game_in)
    message = await ctx.channel.fetch_message(message.id)
    
    users_playing_bj = []
    users = [user async for user in message.reactions[0].users()]
    for user in users:
        if user == bot.user:
            continue
        users_playing_bj.append(str(user))
    
    if len(users_playing_bj) < 1:
        await ctx.send("Noone joined the table! :( ",delete_after=info_delete_after_seconds)
        return None

    #initialize bj users
    bj_players = []

    for user in users_playing_bj:
        try:
            player = bj.load_player_from_file(user)
        except:
            player = bj.BlackjackPlayer(user, starting_money)
            bj.save_player_to_file(player)

        if player.money >= min_bet:
            bj_players.append(player)
        else:
            await ctx.send(f"Sorry {user}, You have only {player.money}!\n minimal bet is {min_bet}",delete_after=info_delete_after_seconds)
    
    if len(users_playing_bj) < 1:
        await ctx.send("No players at the table! ",delete_after=info_delete_after_seconds)
        return None
    
    #initialize bet table
    for player in users_playing_bj:
        if player not in bet_size_table.keys():
            bet_size_table[player] = min_bet
    
    for player in bj_players:
        if player.money < bet_size_table[player.name]:
            await ctx.send(f"{user}, Your bet was set at {bet_size_table_game[player.name]} but you only have {player.money}\nSetting your bet at the minimum ({min_bet})",delete_after=info_delete_after_seconds)
            bet_size_table[player.name] = min_bet

    game = bj.BlackjackGame()

    for player in bj_players:
        game.add_player_to_game(player)
    
    string = "(Change your bets with !bet size [amount])\n"

    for player in bj_players:
        string += f"       -{player.name} bet: {bet_size_table[player.name]}\n"
    string += "------------------------------------------------------------"

    await ctx.send(string,delete_after=delete_after_seconds)
    bet_size_table_game = bet_size_table.copy()
    await game.start_game_discord(ctx, bet_size_table_game)
    
    await asyncio.sleep(4)
    await start_blackjack_game(ctx) # start game again!

    
    


bot.run(token)