import discord
import asyncio
from discord import Intents
from discord.ext import commands
from discord.ext.commands import Context, Bot

from dotenv import load_dotenv
import os

import bot_game_commands
import bot_money_commands

#load .env file
load_dotenv(dotenv_path="etc/.env")

#initialize bot
intents: Intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
intents.messages = True
intents.guilds = True

bot: Bot = Bot(command_prefix='!', intents=intents, help_command=None)
bot_game_commands.setup(bot) # import commands from other files
bot_money_commands.setup(bot)

info_delete_after_seconds: int = 30

@bot.command("help")
async def help(ctx: Context) -> None:
    user: str = str(ctx.message.author)
    await ctx.message.delete()
    
    command_list: list[str] = [
        "!daily -> Gives you a daily reward of {daily_reward} (renewable at midnight)",
        "!balance -> Returns your current balance",
        "!balance all -> Returns the balances of all players",
        "!blackjack -> Starts a blackjack game",
        "!bet size [amount] -> Changes your bet size to the provided amount",
        "!give [player name] [amount] -> Transfers an amount of money from your account to the provided users",
        "!all in -> Changes your bet size to the maximum allowed",
        "!roulette -> starts roulette game"
    ]

    string: str = "-------------------- available commands --------------------"
    for command in command_list:
        string += command + "\n"
    string += "-----------------------------------------------------------"
    await ctx.send(string, delete_after=info_delete_after_seconds)


if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
