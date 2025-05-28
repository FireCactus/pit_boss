from discord.ext.commands import Context
from discord import Message
import asyncio
from ayncio import Coroutine
from typing import NamedTuple


async def send_vanishing_message(context: Context, string: str) -> Message:
    ''' 
    Sends a text message through discord that will delete after _delete_message_after and returns the message object
    '''
    return await context.send(string, delete_after=self._delete_message_after)


async def send_persistant_message(context: Context, string: str) -> Message:
    ''' 
    Sends a text persistant message through discord nad returns the message object
    '''
    return await context.send(string)


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

async def refresh_message(context: Context, message: Message) -> Message:
    return await context.channel.fetch_message(message.id)

async def add_reactions_to_message(message: Message, reactions: list[str]) -> None:
    tasks: list[Coroutine[None, None, None]] = []
    for reaction in reactions:
        tasks.append(message.add_reaction(reaction))
    
    await asyncio.gather(*tasks)


async def get_user_reactions_on_message(message: Message) -> dict[str, list[str]]:
    # this method can only fetch one message reaction at a time so it can be slow with multiple reactions
    # its upside is that it will be harder to hit discords api limit

    user_reactions: dict[str, list[str]] = {}
    for reaction in message.reactions:
        try:
            async for user in reaction.users():
                if user.bot:
                    continue  # Skip bot reactions
                if user.name not in user_reactions:
                    user_reactions[user.name] = [] # add entry if missing

                user_reactions[user.name].append(str(reaction.emoji))
        except Exception as e:
            print(f"Error fetching users for reaction {reaction}: {e}")

    return user_reactions



async def get_user_reactions_on_message_parralelized(message: Message) -> dict[str, list[str]]:
    # 'better' version of get_user_reactions_on_message. grabs all reaction users in parralel. good for making responsive stuff
    # be aware of discords api call limit when using
    
    user_reactions: dict[str, set[str]] = {}

    async def fetch_users_for_reaction(reaction):
        try:
            async for user in reaction.users():
                if user.bot:
                    continue
                user_reactions.setdefault(user.name, set()).add(str(reaction.emoji))
        except Exception as e:
            print(f"Error fetching users for reaction {reaction}: {e}")

    await asyncio.gather(*(fetch_users_for_reaction(r) for r in message.reactions))
    return {u: list(rs) for u, rs in user_reactions.items()}


async def send_standard_join_game_message(context: Context, message_text: str, reactions: list[str], retrieve_after_sec: int) -> dict[str, list[str]]:
    '''
    Sends the 'games starts in x seconds, click reaction to join' message and after a delay returns who clicked what reaction
    '''
    
    join_message_delete_offset: int = 5 # gives time for the bot to gather the reactions before deleting the message

    join_message: Message = send_vanishing_message(context, message_text, retrieve_after_sec+join_message_delete_offset)
    add_reactions_to_message(join_message, reactions)
    await asyncio.sleep(retrieve_after_sec)
    join_message = refresh_message(join_message)

    return get_user_reactions_on_message(join_message)
