from discord import *
from discord.ext import commands
from discord.ext.commands import Context, Bot
from typing import *
import asyncio

from player.Player import Player
from bot_commands import discord_utilities as du 


def setup(bot: Bot) -> None:

    @bot.command("")