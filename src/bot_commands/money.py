from discord.ext import commands
from discord.ext.commands import Context, Bot
from typing import Optional

from games.Player import Player
from database.PlayersDatabase import PlayersDatabase
db = PlayersDatabase()

info_delete_after_seconds: int = 15

def setup(bot: Bot) -> None:

    @bot.command("daily")
    async def receive_dailty(ctx: Context) -> None:
        user: str = str(ctx.message.author)
        player: Player = Player(user)
        await ctx.message.delete()
        
        try:
            player.receive_daily()
            await ctx.send(f" {player.name} received their daily reward! {player._daily_amount} added to balance ")
        except ValueError as e:
            await ctx.send(f"Unable to give daily to {player.name}\nReason: {e}", delete_after=info_delete_after_seconds)


    @bot.command("give")
    async def transfer_money(ctx: Context, arg_1: str, arg_2: str) -> None:
        user: str = str(ctx.message.author)
        from_player: Player = Player(user)
        await ctx.message.delete()


        to_user: str = arg_1
        amount: int = int(arg_2)

        #check if to player exists
        if db.check_if_player_exists(to_user) ==  False:
            await ctx.send(f"Sorry, player with name {to_user} does not exist", delete_after=info_delete_after_seconds)
            return None            

        to_player: Player = Player(to_user)

        #check if from player has enough money
        balance: int = from_player.get_balance()
        if balance < amount:
            await ctx.send(f"Sorry, you only have {balance}", delete_after=info_delete_after_seconds)
            return None 

        from_player.modify_balance(-amount)
        to_player.modify_balance(amount)
        await ctx.send(f"Transferred {amount} from {from_player.name} to {to_player.name}",delete_after=info_delete_after_seconds)
        
        
    @bot.command("balance")
    async def get_user_balance(ctx: Context, arg_1: Optional[str]) -> None:
        user: str = str(ctx.message.author)
        await ctx.message.delete()
        
        if arg_1 == "all":

            string = "---- All players money ----\n"
            for username in db.get_all_players():
                listed_player: Player = Player(username)
                string += f"{listed_player.name}   {listed_player.get_balance()}\n---------------------------n"
            await ctx.send(string)
        else:
            player: Player = Player(user)
            await ctx.send(f"{player.name} balance: {player.get_balance()}",delete_after=info_delete_after_seconds)