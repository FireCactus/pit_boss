from discord.ext import commands

WESKER_GIF = "media/wesker-no-wesker-no-no.gif"

def setup(bot):
    @bot.command("daily")
    async def change_bet_to_max(ctx):
        user = str(ctx.message.author)

        init_player(user)
        player = g_player.load_player_from_file(user)    

        await ctx.message.delete()

        if player.received_daily:
            await ctx.send(f"Sorry {player.name}, You already received your daily reward!",delete_after=info_delete_after_seconds)
            return None
        
        player.received_daily = True
        player.money += daily_reward

        g_player.save_player_to_file(player)
        await ctx.send(f"{player.name} received their daily reward! {daily_reward} added to balance")



    @bot.command("give")
    async def transfer_money(ctx, arg_1, arg_2):
        #init from user
        user = str(ctx.message.author)
        await ctx.message.delete()
        init_player(user)

        
        from_user =  g_player.load_player_from_file(user)
        to_user = arg_1
        try:
            amount = int(arg_2)
        except:
            await ctx.send(f"{arg_2} is an invalid amount",delete_after=info_delete_after_seconds)
        
        player_names = []
        for player in g_player.load_all_players():
            player_names.append(player.name)
        
        if to_user not in player_names:
            await ctx.send(f"No such User as {to_user}",delete_after=info_delete_after_seconds)
        else:
            to_user = g_player.load_player_from_file(to_user)
        
        if to_user.name == from_user.name:
            await ctx.send(f"You can't send money to yourself",delete_after=info_delete_after_seconds)
            return

        if amount > from_user.money:
            await ctx.send(f"Insufficient money! You only have {from_user.money}",delete_after=info_delete_after_seconds)
        elif amount < 0:
            with open(WESKER_GIF, 'rb') as f:
                gif = discord.File(f)
                await ctx.send(file=gif)
        else:
            from_user.money -= amount
            to_user.money += amount
            await ctx.send(f"Transferred {amount} from {from_user.name} to {to_user.name}",delete_after=info_delete_after_seconds)

            g_player.save_player_to_file(from_user)
            g_player.save_player_to_file(to_user)

            

    @bot.command("balance")
    async def get_user_balance(ctx, arg_1=None):
        user = str(ctx.message.author)
        await ctx.message.delete()
        
        init_player(user)
        player = g_player.load_player_from_file(user)   
    
        if arg_1 == "all":
            string = "---- All players money ----\n"
            for player in g_player.load_all_players():
                string += f"{player.name}   {player.money}\n--------------------\n"
            await ctx.send(string,delete_after=info_delete_after_seconds)
        else:
            await ctx.send(f"{user} balance: {player.money}",delete_after=info_delete_after_seconds)