import time
import asyncio
import discord

from collections.abc import Coroutine
from discord.ext.commands import Context, Bot
from discord import Message, User, Reaction, File

from typing import *




vanishing_message_timer: int = 15
ask_message_timeout: int = 45

DISCORD_MESSAGE_CHAR_LIMIT = 2000

async def send_vanishing_message(context: Context, string: str, time_to_vanish: int = vanishing_message_timer) -> list[Message]:
    '''
    Sends text messages through Discord, splitting the message into chunks
    of <=2000 characters (Discord limit), all set to auto-delete after a delay.
    Returns the last Message object.
    '''
    message: Message

    # Split the message into 2000-char chunks
    while string:
        chunk = string[:DISCORD_MESSAGE_CHAR_LIMIT]
        # Try not to break in the middle of a word or line
        if len(string) > DISCORD_MESSAGE_CHAR_LIMIT:
            last_newline = chunk.rfind('\n')
            last_space = chunk.rfind(' ')
            split_index = max(last_newline, last_space)
            if split_index > 0:
                chunk = string[:split_index]
        else:
            split_index = len(chunk)

        message = await context.send(chunk.strip(), delete_after=time_to_vanish)
        string = string[split_index:].lstrip()

    return message
    

async def send_persistant_message(context: Context, string: str) -> Message:
    ''' 
    Sends a text persistant message through discord nad returns the message object
    '''
    return await context.send(string)


async def send_persistant_file_by_path(context: Context, path: str) -> Message:
    with open(path, 'rb') as f:
        file: File = discord.File(f)
        await context.send(file=file)

async def send_vanishing_file_by_path(context: Context, path: str, time_to_vanish:int=vanishing_message_timer) -> Message:
    with open(path, 'rb') as f:
        file: File = discord.File(f)
        await context.send(file=file, delete_after=time_to_vanish)


async def edit_message(message: Message, string: str) -> Message:
    ''' 
    Sends a text persistant message through discord nad returns the message object
    '''
    return await message.edit(content=string)


async def delete_message(message: Message) -> None:
    ''' 
    Tries to delete the provided message
    '''
    try:
        await message.delete()
    except discord.NotFound:
        pass #if failed to delete a message because it doesnt exist then dont throw an error

async def refresh_message(message: Message) -> Message:
    return await message.channel.fetch_message(message.id)


async def add_reactions_to_message(message: Message, reactions: list[str]) -> None:
    tasks: list[Coroutine[None, None, None]] = []
    for reaction in reactions:
        tasks.append(message.add_reaction(reaction))
    
    await asyncio.gather(*tasks)


async def get_user_reactions_on_message(message: Message) -> Dict[User, list[str]]:
    # this method can only fetch one message reaction at a time so it can be slow with multiple reactions
    # its upside is that it will be harder to hit discords api limit

    user_reactions: Dict[User, list[str]] = {}
    for reaction in message.reactions:
        try:
            async for user in reaction.users():
                if user.bot:
                    continue  # Skip bot reactions
                if user.name not in user_reactions:
                    user_reactions[user] = [] # add entry if missing

                user_reactions[user].append(str(reaction.emoji))
        except Exception as e:
            print(f"Error fetching users for reaction {reaction}: {e}")

    return user_reactions


async def get_user_reactions_on_message_parralelized(message: Message) -> Dict[User, list[str]]:
    # 'better' version of get_user_reactions_on_message. grabs all reaction users in parralel. good for making responsive stuff
    # be aware of discords api call limit when using
    
    user_reactions: Dict[User, set[str]] = {}

    async def fetch_users_for_reaction(reaction: Reaction) -> None:
        try:
            async for user in reaction.users():
                if user.bot:
                    continue
                user_reactions.setdefault(user, set()).add(str(reaction.emoji))
        except Exception as e:
            print(f"Error fetching users for reaction {reaction}: {e}")

    await asyncio.gather(*(fetch_users_for_reaction(r) for r in message.reactions))
    return {u: list(rs) for u, rs in user_reactions.items()}


async def send_standard_join_game_message(context: Context, message_text: str, reactions: list[str], retrieve_after_sec: int) -> Dict[User, list[str]]:
    '''
    Sends the 'games starts in x seconds, click reaction to join' message and after a delay returns who clicked what reaction
    '''
    
    join_message_delete_offset: int = 5 # gives time for the bot to gather the reactions before deleting the message

    join_message: Message = await send_vanishing_message(context, message_text, retrieve_after_sec+join_message_delete_offset)
    await add_reactions_to_message(join_message, reactions)
    await asyncio.sleep(retrieve_after_sec)

    join_message = await refresh_message(join_message)
    return await get_user_reactions_on_message(join_message)

async def send_message_and_wait_for_user_choice(context: Context, message_text: str, reactions: list[str], user: User, timeout: int=ask_message_timeout) -> Optional[str]:
    '''
        Creates a message and adds reactions to it.
        if a designated player has clicked any of the reactions returns the reaction (string).
        if the designated player failed to click any reaction within the timeout it returns None
    '''

    ask_message: Message = await send_persistant_message(context, message_text)
    await add_reactions_to_message(ask_message, reactions)

    start_time: float = time.time()
    while time.time() - start_time < timeout:
        await asyncio.sleep(1) # wait a second between message checks
        ask_message = await refresh_message(ask_message)
        
        reaction_users: Dict[User, list[str]] = await get_user_reactions_on_message(ask_message)
        if user in reaction_users.keys():
            if reaction_users[user][0] in reactions:
                await delete_message(ask_message)
                return reaction_users[user][0] # return the first one if user clicked many
    

    await delete_message(ask_message)
    return None

async def get_discord_user_from_id(bot: Bot ,discord_id: int) -> User:
    return await bot.fetch_user(discord_id)


