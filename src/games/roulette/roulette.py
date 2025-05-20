from games import game_player as g_player

import discord
import asyncio
import random

black_emoji = "⬛"
red_emoji = "🟥"
green_emoji = "🟩"
white_emoji = "⬜"
up_emoji = "⬆️"
down_emoji = "⬇️"

min_spin = 0
max_spin = 37

payout_table = {
    "correct_red_black_guess":2,
    "correct_green_guess":37,
    "even_odd_payout":2,
    "green_when_not_chosen":0.5 #when you pick red or black but the roulette comes up green
}

class RouletteGame:
    def __init__(self, min_bet=25, max_bet=1000, delete_messages_after_seconds=60):
        self.players = []

        self.min_bet = min_bet
        self.max_bet = max_bet
        self.delete_messages_after_seconds = delete_messages_after_seconds

    def add_player_to_game(self, player):

        if player is g_player.GamePlayer:
            raise ValueError(f"player is not GamePlayer but {type(player)}")
            
        
        elif player.money < self.min_bet:
            raise ValueError(f"Player doesnt have enough money to play! \n minimal bet is {self.min_bet}, player has {player.money}")
        
        elif player not in self.players:
            self.players.append(player)

            
    def remove_player(self, player):
        if player not in self.players:
            return None

        self.players.remove(player)

    async def start_game_discord(self, ctx, bet_size_table):
        
        #remove money from players
        for player in self.players:
            player.money -= bet_size_table[player.name]

        #init the strings for numbers and emoji spinnings
        boxes_string = black_emoji + red_emoji
        boxes_string = green_emoji + boxes_string*18
        numbers_list =[0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]

        numbers_string = ""
        for number in numbers_list:
            if number < 10:
                numbers_string += f"{number}  |"
            else:
                numbers_string += f"{number} |"

        spin_msg = await ctx.send(white_emoji*18 + down_emoji + white_emoji *18 + "\n" + boxes_string+"\n" + numbers_string + "\n" + white_emoji*18 + up_emoji + white_emoji *18)

        spin_amount = random.randrange(min_spin, max_spin)
        spin_amount += 37 #always make the spin at least one revolution

        #spin the wheel
        for _ in range(spin_amount):
            await asyncio.sleep(1.01)

            #move numbers to the left
            numbers_list.append(numbers_list.pop(0))

            #recrete the numbers string
            numbers_string = ""
            for number in numbers_list:
                if number < 10:
                    numbers_string += f"{number}  |"
                else:
                    numbers_string += f"{number} |"

            #move emojis to the left
            boxes_string = boxes_string[1:] + boxes_string[0]  #rotate the string by 1 to the left
            await spin_msg.edit(content=white_emoji*18 + down_emoji + white_emoji *18 + "\n" + boxes_string+"\n"+ numbers_string + "\n" + white_emoji*18 + up_emoji + white_emoji *18)

        #get result
        result_color = boxes_string[18]
        result_number = numbers_list[18]
        if result_number == 0:
            result_number = "chuj"

        elif result_number % 2 == 0:
            result_number = "even"
        
        elif result_number % 2 == 1:
            result_number = "odd" 

        end_msg = await ctx.send(f"roulette has stopped!\n Result is: {result_color}{result_number}!")
        
    
        #payout any wins
        for player in self.players:
            #check for color win
            
            if player.roulette_pick_color == result_color:
                if result_color == green_emoji:
                    payout = bet_size_table[player.name] * payout_table['correct_green_guess']
                else:
                    payout = bet_size_table[player.name] * payout_table['correct_red_black_guess']
                
                player.money += payout
                await ctx.send(f"{player.name} Won {payout}!")
            elif player.roulette_pick_color != None:
                await ctx.send(f"{player.name} Lost {bet_size_table[player.name]}")

            #check for number win (even, odd)
            elif player.roulette_pick_number == result_number:
                payout = bet_size_table[player.name] * payout_table['even_odd_payout']
                player.money += payout
                await ctx.send(f"{player.name} Won {payout}!")
            elif player.roulette_pick_number != None:
                await ctx.send(f"{player.name} Lost {bet_size_table[player.name]}")

            #save players to file
            g_player.save_player_to_file(player)
        
        await asyncio.sleep(5)

        await spin_msg.delete()
        await end_msg.delete()



                