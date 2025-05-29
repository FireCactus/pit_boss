from discord.ext import commands
from discord.ext.commands import Context, Bot
from typing import Optional

from player.Player import Player
from database.PlayersDatabase import PlayersDatabase
db = PlayersDatabase()

info_delete_after_seconds: int = 15

def setup(bot: Bot) -> None:
    
    @bot.command("bet")
    async def change_player_bet(ctx: Context, arg_1: str, arg_2: str) -> None:
        if arg_1 == "size":
            player: Player = Player(ctx.message.author)
            await ctx.message.delete()
           
            amount = int(arg_2)
            try:
                player.change_bet(amount)
                await ctx.send(f"Bet size for {player.name} changed to {amount}", delete_after=info_delete_after_seconds)
            except ValueError as e:
                await ctx.send(f"Bet size for {player.name} Unchanged!\nReason: {e}", delete_after=info_delete_after_seconds)


    @bot.command("all")
    async def change_bet_to_max(ctx: Context, arg_1: str) -> None:
        if arg_1 == "in":
            player: Player = Player(ctx.message.author)
            await ctx.message.delete()

            current_balance = player.get_balance()
            try:
                player.change_bet(current_balance)
                await ctx.send(f"Bet size for {player.name} changed to {current_balance}", delete_after=info_delete_after_seconds)
            except ValueError as e:
                await ctx.send(f"Bet size for {player.name} Unchanged!\nReason: {e}", delete_after=info_delete_after_seconds)


    @bot.command("daily")
    async def receive_dailty(ctx: Context) -> None:
        player: Player = Player(ctx.message.author)
        await ctx.message.delete()
        
        try:
            player.receive_daily()
            await ctx.send(f" {player.name} received their daily reward! {player._daily_amount} added to balance ")
        except ValueError as e:
            await ctx.send(f"Unable to give daily to {player.name}\nReason: {e}", delete_after=info_delete_after_seconds)


    @bot.command("give")
    async def transfer_money(ctx: Context, arg_1: str, arg_2: str) -> None:
        from_player: Player = Player(ctx.message.author)
        await ctx.message.delete()


        to_user: User = ctx.message.mentions[0]
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
        await ctx.message.delete()
        if arg_1 == "all":

            string = "---- All players money ----\n"
            for discord_id in db.get_all_players():
                listed_player: Player = Player(get_discord_user_from_id(bot, discord_id))
                string += f"{listed_player.name}   {listed_player.get_balance()}\n---------------------------n"
            await ctx.send(string)
        else:
            player: Player = Player(ctx.message.author)
            await ctx.send(f"{player.name} balance: {player.get_balance()}",delete_after=info_delete_after_seconds)