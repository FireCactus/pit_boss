import discord
import asyncio
from discord import Intents
from discord.ext import commands
from discord.ext.commands import Context, Bot

from dotenv import load_dotenv
import os

from bot_commands import discord_utilities as du
from bot_commands.games import blackjack, roulette
from bot_commands import money
#load .env file
load_dotenv(dotenv_path="etc/.env")

#initialize bot
intents: Intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
intents.messages = True
intents.guilds = True

bot: Bot = Bot(command_prefix='!', intents=intents, help_command=None)

blackjack.setup(bot) # import commands from other files
roulette.setup(bot)
money.setup(bot)

info_delete_after_seconds: int = 30

@bot.command("help")
async def help(ctx: Context) -> None:
    user: str = str(ctx.message.author)
    await du.delete_message(ctx.message)
    
    command_list: list[str] = [
        f"!daily -> Gives you a daily reward of 100 (renewable at midnight)",
        f"!balance -> Returns your current balance",
        f"!balance all -> Returns the balances of all players",
        f"!blackjack -> Starts a blackjack game",
        f"!bet size [amount] -> Changes your bet size to the provided amount",
        f"!give [player name] [amount] -> Transfers an amount of money from your account to the provided users",
        f"!all in -> Changes your bet size to the maximum allowed",
        f"!roulette -> starts roulette game"
    ]

    string: str = "-------------------- available commands --------------------\n"
    for command in command_list:
        string += command + "\n"
    string += "-----------------------------------------------------------"
    await du.send_vanishing_message(ctx, string, info_delete_after_seconds)


if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
