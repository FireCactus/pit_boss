import discord
import asyncio
from discord.ext import commands

from dotenv import load_dotenv
import os

import bot_game_commands
import bot_money_commands

#load .env file
load_dotenv(dotenv_path="etc/.env")

#initialize bot
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
bot_game_commands.setup(bot) # import commands from other files
bot_money_commands.setup(bot)

delete_after_seconds = 60
info_delete_after_seconds = 15


def init_player(user):
    try:
        player = g_player.load_player_from_file(user)
    except:
        player = g_player.GamePlayer(user, starting_money)
        g_player.save_player_to_file(player)

@bot.command("help")
async def help(ctx):
    user = str(ctx.message.author)
    await ctx.message.delete()
    command_list = [
        "!daily -> Gives you a daily reward of {daily_reward} (renewable at midnight)",
        "!balance -> Returns your current balance",
        "!balance all -> Returns the balances of all players",
        "!blackjack -> Starts a blackjack game",
        "!bet size [amount] -> Changes your bet size to the provided amount",
        "!give [player name] [amount] -> Transfers an amount of money from your account to the provided users",
        "!all in -> Changes your bet size to the maximum allowed",
        "!roulette -> starts roulette game"
    ]

    string = "-------------------- available commands --------------------"
    for command in command_list:
        string += command + "\n"
    string += "-----------------------------------------------------------"
    await ctx.send(string, delete_after=info_delete_after_seconds*2)


if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
