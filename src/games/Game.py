from typing import *
from abc import ABC, abstractmethod


# all interaction happens outside of this class
# this class is only used to handle game frames.

#move all message functions to a utils class

class Game(ABC):
    _payout_table: Dict[str,float] # how much to pay out for each scenario

    def __init__(self) -> None:
        pass

    def init_game_statistics(self) -> None:
        ''' initializes all tracked statistics at 0'''
        for player_name in self.players:
            for statistic_name in self._tracked_statistics:
                self._player_statistics[player_name][statistic_name] = 0

    
    def modify_player_statistic(self, player_name: str, statiscic_name: str, operation: StatisticOperations, amount:int) -> None:
        if operation == StatisticOperations.ADD:
            self._player_statistics[player_name][statiscic_name] += amount
        
        elif operation == StatisticOperations.SUBTRACT:
            self._player_statistics[player_name][statiscic_name] -= amount
        
        elif operation == StatisticOperations.SET_TO:
            self._player_statistics[player_name][statiscic_name] = amount
    

    async def send_vanishing_message(self, string: str) -> Message:
        ''' 
        Sends a text message through discord that will delete after _delete_message_after and returns the message object
        '''
        return await ctx.send(string, delete_after=self._delete_message_after)


    async def send_persistant_message(self, string: str) -> Message:
        ''' 
        Sends a text persistant message through discord nad returns the message object
        '''
        return await ctx.send(string)
    

    async def edit_message(self, message: Message, string: str) -> Message:
        ''' 
        Sends a text persistant message through discord nad returns the message object
        '''
        return await message.edit(content=string)
    

    async def delete_message(self, message: Message) -> None:
        ''' 
        Tries to delete the provided message
        '''
        try:
            await message.delete()
        except discord.NotFound:
            pass #if failed to delete a message because it doesnt exist then dont throw an error
    
    @abstractmethod
    async def play(self) -> None:
        '''
        This function starts the game on discord.
        The input is a list of players and their bets (Object provided by the particular game class)
        '''
        
        pass
