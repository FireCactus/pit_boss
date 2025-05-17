from card_deck import Deck
from card import Card
import yaml
import math
import time
import os
import discord
import asyncio

stand_reaction = "❌"
hit_reaction = "👆"
split_reaction = "↔️"
double_reaction = "🔥"


clear = lambda: os.system('clear')

DECKS_IN_PLAY = 6 # how many decks in the shoe
PLAYER_STARTER_MONEY = 100

PAYOUT_TABLE={
"normal_win":2,
"draw":1,
"blackjack":2.5
}

delete_after_seconds = 60


class BlackjackPlayer:
    def __init__(self, name, money=0, hands=[], received_daily=False):
        self.name = name
        self.money = money
        self.received_daily = received_daily
        
        self.hands = hands # list of lists containing cards
        self.dealer_cards = []


def load_all_players(file="players.yaml"):
    bj_players = []
    with open(file, "r") as stream:
        players = yaml.load_all(stream, yaml.FullLoader)

        for player in players:
            bj_player = BlackjackPlayer(player["name"], player['money'], received_daily=player['received_daily'])
            bj_players.append(bj_player)
    return bj_players

            

def load_player_from_file(player_name, file="players.yaml"):

    with open(file, "r") as stream:
        players = yaml.load_all(stream, yaml.FullLoader)

        for player in players:
            if player["name"] == player_name:
                bj_player = BlackjackPlayer(player_name, player['money'], received_daily=player['received_daily'])
                return bj_player
        raise ValueError(f"Player {player_name} doesnt exist in player file")


def save_player_to_file(bj_player, file="players.yaml"):
    
    with open(file, "r") as stream:
        players = list(yaml.load_all(stream, yaml.FullLoader))

        # Check if the player exists, and update or append
        updated = False
        for player in players:
            if player["name"] == bj_player.name:
                player["money"] = bj_player.money
                player['received_daily'] = bj_player.received_daily
                updated = True
                break

        if not updated:
            players.append({"name": bj_player.name, "money": bj_player.money, 'received_daily':bj_player.received_daily})

    # Write back all players to the file
    with open(file, "w") as stream:

        yaml.dump_all(players, stream)


    

def calculate_blackjack_hand_value(cards):

        try:
            cards = cards['cards']
        except:
            pass

        total_value = 0
        aces = 0
        for card in cards:
            if card.face_down == True:
                continue
            
            value = card.get_value()
            if value == "A":
                total_value += 11
                aces += 1 # save aces for later as we need to know whether they will be a 1 or 11
            
            elif value in ["J", "Q", "K"]:
                total_value += 10
            else:
                total_value += int(value)
        
        for _ in range(aces):
            if total_value > 21:
                total_value -= 10 # change the ace to a 1 if the count is above 21
        
        return total_value
            
class BlackjackGame:
    def __init__(self, shoe_size=6, min_bet=25, max_bet=1000, max_players=10):
        self.players = []
        self.shoe = self.construct_deck(shoe_size) # Deck object

        self.min_bet = min_bet
        self.max_bet = max_bet
        self.max_players = max_players

        self.dealer_cards = []

    def construct_deck(self, n_decks):
        shoe = Deck(type="normal")
        cards = shoe.cards.copy()

        if n_decks >= 2:

            for i in range(n_decks - 1):
                shoe.insert(cards)

        shoe.shuffle()
        return shoe

    def add_player_to_game(self, player):
        if len(self.players) > self.max_players:
            raise ValueError("Not enough room at the table!\n the table can only fit {self.max_players} players")

        if type(player) is BlackjackPlayer:
            if player.money < self.min_bet:
                raise ValueError(f"Player doesnt have enough money to play! \n minimal bet is {self.min_bet}, player has {player.money}")
            if player not in self.players:
                self.players.append(player)
        else:
            raise ValueError(f"player is not BlackjackPlayer but {type(player)}")

    def remove_player(self, player):
        if player not in self.players:
            return
        
        self.players.remove(player)
    
    def ask_player_for_bet_cli(self, player):
        clear()
        while True:

            bet = int(input(f"{player.name} bet ({player.money}): "))
            if bet < self.min_bet or bet > self.max_bet:
                print(f"Invalid bet size. minimal bet is {self.min_bet} maximal bet is {self.max_bet}")
                continue
            
            
            if bet > player.money:
                print(f"insufficient funds. You only have {player.money}")
                continue
            
            break
        
        player.money -= bet
        return bet

    def print_table(self, end=False):
        clear()
        if end:
            print("---------   END OF HAND  -------")

        print(f"Dealer: ({calculate_blackjack_hand_value(self.dealer_cards)})", end=None)
        for card in self.dealer_cards:
            if card.face_down == False:
                value, color = card.get_value_and_color()
                print(f"{value} of {color}, ", end=None)
            else:
                print("[?]")

        print("")
        for player in self.players:
            print(f"{player.name}: ", end=None)
            for hand in player.hands:
                print(f"({calculate_blackjack_hand_value(hand)})")
                for card in hand:
                    value, color = card.get_value_and_color()
                    print(f"{value} of {color}, ", end=None)   
                print("")
    
    def get_player_decision(self, player, hand, bet):
        self.print_table()
        moves = ["hit", "stand"]
        if player.money >= bet:

            if len(hand) == 2:
                if hand[0].get_value() == hand[1].get_value(): 
                    moves.append("split")
                elif hand[0].get_value() in ["J","Q","K","10"] and hand[1].get_value() in ["J","Q","K","10"]: 
                    moves.append("split")
            
            if len(hand) == 2:
                moves.append("double")


        while True:
            print("-------------------")
            print(f"{player.name} ({calculate_blackjack_hand_value(hand)}): ")
            for card in hand:
                value, color = card.get_value_and_color()
                print(f"{value} of {color}, ", end=None)   
            print("")
            
            for move in moves:
                print(move, end="  ")
            print("")
                

            dec = input("what do you want to do?\n")
            if dec not in moves:
                print("Invalid move choice")
                continue
            return dec

    def play_dealer(self):
        Dealer_stop=17
        
        self.dealer_cards[1].face_down = False # turn over the face down card
        self.print_table(end=True)

        while calculate_blackjack_hand_value(self.dealer_cards) < Dealer_stop:
            time.sleep(1)   
            self.dealer_cards.append(self.shoe.draw_card(face_down=False))
            self.print_table(end=True)
            
    def deal_initial_cards(self, player_bets):
        
        # give each player a card
        for player in self.players:
            card = self.shoe.draw_card(face_down=False)
            card.face_down = False #ensure it is face down

            player.hands = [] # clear player hands 
            hand = {'bet':player_bets[player.name],
                    "cards":[card]
                    }
            player.hands.append(hand)

        # give the dealer a card
        card = self.shoe.draw_card(face_down=False)
        card.face_down = False #ensure it is face down
        self.dealer_cards.append(card)

        # give the players their second card
        for player in self.players:
            card = self.shoe.draw_card(face_down=False)
            card.face_down = False #ensure it is face down

            player.hands[0]['cards'].append(card)
        
        # give the dealer the second card face down 
        self.dealer_cards.append(self.shoe.draw_card(face_down=True))

    
    def start_game_cli(self): # plays one hand of BlackJack
        if len(self.players) == 0:
            raise ValueError(f"need at least 1 player to start game")
        
        playing_players = self.players.copy()

        player_bets = {}
        for player in self.players:
            player_bets[player.name] = self.ask_player_for_bet_cli(player)
        
        # initial dealing ---------
        self.deal_initial_cards()

        #ensure all player cards are face up
        for player in self.players:
            for hand in player.hands:
                for card in hand:
                    card.face_down = False



        self.print_table()
        #check if anyone got a blackjack
        
        for player in self.players:
            for hand in player.hands:
                total = calculate_blackjack_hand_value(hand)
                if total == 21:                 
                    payout = math.floor(player.hands[0]['bet'] * PAYOUT_TABLE["blackjack"])
                    print(f"{player.name} got a blackjack winning {payout}!")
                    player.money += payout
                    playing_players.remove(player)
                    input()

        #play with each player
        for player in playing_players:
            self.print_table()
            
            for i, hand in enumerate(player.hands):
                decision = ""

                while True:
                    decision = self.get_player_decision(player, player.hands[i], player_bets[player.name])
                    
                    if decision == "hit":
                        player.hands[i].append(self.shoe.draw_card(face_down=False))

                        if calculate_blackjack_hand_value(player.hands[i]) >= 21:
                            break

                    elif decision == "stand": 
                        break

                    elif decision == "double": 
                        player.money -= player_bets[player.name]
                        player_bets[player.name] = player_bets[player.name]*2
                        player.hands[i].append(self.shoe.draw_card(face_down=False))
                        break

                    elif decision == "split": 
                        player.money -= player_bets[player.name]
                        player.hands.append([player.hands[i][1]])
                        player.hands[i] = [player.hands[i][0]]


        # play the dealer
        self.play_dealer()

        #check any payouts:
        dealer_total = calculate_blackjack_hand_value(self.dealer_cards)
        if dealer_total > 21:
            for player in playing_players:
                for hand in player.hands:
                    if calculate_blackjack_hand_value(hand) <= 21:
                        payout = math.floor(player_bets[player.name] * PAYOUT_TABLE["normal_win"])
                        print(f"{player.name} Wins {payout}")
                        player.money += payout
        else:
            for player in playing_players:
                for hand in player.hands:
                    hand_value = calculate_blackjack_hand_value(hand)

                    if hand_value > 21:
                        continue

                    if hand_value > dealer_total:
                        payout = math.floor(player_bets[player.name] * PAYOUT_TABLE["normal_win"])
                        print(f"{player.name} Wins {payout}")
                        player.money += payout
                    
                    elif hand_value == dealer_total:
                        payout = math.floor(player_bets[player.name] * PAYOUT_TABLE["draw"])
                        print(f"{player.name} matched the dealer. draw payout: {payout}")
                        player.money += payout
                    
                    time.sleep(1)
                       
        
        #save players to file:
        for player in self.players:
            save_player_to_file(player)
        
        self.players = []
        self.dealer_cards = []

        for card in self.shoe.cards: # turn over any cards that might be face down in the deck
            if card.face_down:
                card.face_down = False

        input()

    async def play_dealer_discord(self, ctx):
        Dealer_stop=17
        
        self.dealer_cards[1].face_down = False # turn over the face down card
        table = await self.send_bj_table_to_discord(ctx)
        await asyncio.sleep(1)

        while calculate_blackjack_hand_value(self.dealer_cards) < Dealer_stop:
            await table.delete()

            await asyncio.sleep(1)  
            
            self.dealer_cards.append(self.shoe.draw_card(face_down=False))
            table = await self.send_bj_table_to_discord(ctx)
        
        for player in self.players:
            for hand in player.hands:
                for card in hand['cards']:
                    if card.face_down == True:
                        await asyncio.sleep(1)  
                        await table.delete()
                        card.face_down = False
                        table = await self.send_bj_table_to_discord(ctx)


    async def start_game_discord(self, ctx, player_bets):

        #remove money from players
        for player in self.players:
            player.money -= player_bets[player.name]


        # initial dealing ---------
        self.deal_initial_cards(player_bets)

        
        # check if anyone got a blackjack
        playing_players = self.players.copy()
        for player in self.players:
            for hand in player.hands:
                total = calculate_blackjack_hand_value(hand)
                if total == 21:                 
                    payout = math.floor(player.hands[0]['bet'] * PAYOUT_TABLE["blackjack"])
                    await ctx.send(f"{player.name} got a blackjack winning {payout}!",delete_after=delete_after_seconds)
                    player.money += payout
                    playing_players.remove(player)


            

        # play with each player
        for player in playing_players:

            for i, hand in enumerate(player.hands):
                decision = ""

                while True:
                    table = await self.send_bj_table_to_discord(ctx)
                    decision = await self.ask_user_for_choice_discord(ctx, player, player.hands[i], player.hands[i]['bet'])
                    await table.delete()
                    
                    if decision == "hit":
                        player.hands[i]['cards'].append(self.shoe.draw_card(face_down=False))

                        if calculate_blackjack_hand_value(player.hands[i]) >= 21:
                            break

                    elif decision == "stand": 
                        break

                    elif decision == "double": 
                        player.money -= player.hands[i]['bet']
                        player.hands[i]['bet'] = player.hands[i]['bet']*2
                        player.hands[i]['cards'].append(self.shoe.draw_card(face_down=True))
                        break

                    elif decision == "split": 
                        player.money -= player.hands[i]['bet']
                        split_card = player.hands[i]['cards'].pop()
                        hand = {'bet': player.hands[i]['bet'],
                                'cards': [split_card]
                        }
                        player.hands.append(hand)
        
        #play with the dealer        
        await self.play_dealer_discord(ctx)

        #check any payouts:
        await ctx.send("------------------------------------------------------------",delete_after=delete_after_seconds)
        dealer_total = calculate_blackjack_hand_value(self.dealer_cards)
        if dealer_total > 21:
            for player in playing_players:
                for hand in player.hands:
                    if calculate_blackjack_hand_value(hand) <= 21:
                        payout = math.floor(hand['bet'] * PAYOUT_TABLE["normal_win"])
                        await ctx.send(f"   {player.name} Wins {payout}",delete_after=delete_after_seconds)
                        player.money += payout
        else:
            for player in playing_players:
                for hand in player.hands:
                    hand_value = calculate_blackjack_hand_value(hand)

                    if hand_value > 21:
                        await ctx.send(f"   {player.name} Loses {hand['bet']}",delete_after=delete_after_seconds)
                        continue

                    if hand_value > dealer_total:
                        payout = math.floor(hand['bet'] * PAYOUT_TABLE["normal_win"])
                        await ctx.send(f"   {player.name} Wins {payout}",delete_after=delete_after_seconds)
                        player.money += payout
                    
                    elif hand_value == dealer_total:
                        payout = math.floor(hand['bet'] * PAYOUT_TABLE["draw"])
                        await ctx.send(f"   {player.name} matched the dealer. draw payout: {payout}",delete_after=delete_after_seconds)
                        player.money += payout
                    
                    elif hand_value < dealer_total:
                        await ctx.send(f"   {player.name} Loses {hand['bet']}",delete_after=delete_after_seconds)
        
        string = "---------------------Current balance------------------------: \n"
        for player in self.players:
            string += f"   {player.name} - {player.money}\n" 

        await ctx.send(string,delete_after=delete_after_seconds)
        
        #save players to file:
        for player in self.players:
            save_player_to_file(player)
        

    async def send_bj_table_to_discord(self, ctx):
        string = ""
        string += f"Dealer: ({calculate_blackjack_hand_value(self.dealer_cards)})\n"
        for card in self.dealer_cards:
            if card.face_down == False:
                value = card.get_value()
                color = card.get_color_emoji()

                string += f"{value}{color}, "
            else:
                string += "[?]\n"

        string += "\n"
        for player in self.players:
            string += f"{player.name}:\n"
            for hand in player.hands:
                for card in hand['cards']:
                    if card.face_down == False:
                        value = card.get_value()
                        color = card.get_color_emoji()
                        string += f"{value}{color}  "
                    else:
                        string += "[?]  "
                
                string += f"-  ({calculate_blackjack_hand_value(hand)})\n"   
        
        message = await ctx.send(string,delete_after=delete_after_seconds)
        return message

    async def ask_user_for_choice_discord(self, ctx, player, hand, bet):
        
        timeout = 30 # if after 30s no choice is made, stand for the player

        message = await ctx.send(f"What do you want to do {player.name}?\nCurrent hand value is {calculate_blackjack_hand_value(hand)}")
        await message.add_reaction(stand_reaction)
        await message.add_reaction(hit_reaction)

        if player.money >= bet:
            hand = hand['cards']
            if len(hand) == 2:
                if hand[0].get_value() == hand[1].get_value(): 
                    await message.add_reaction(split_reaction)
                elif hand[0].get_value() in ["J","Q","K","10"] and hand[1].get_value() in ["J","Q","K","10"]: 
                    await message.add_reaction(split_reaction)
            
            if len(hand) == 2:
                await message.add_reaction(double_reaction)
        
        start_time = time.time()
        waiting = True
        action = 'stand'
        while waiting and time.time() - start_time <= timeout:
            message = await ctx.channel.fetch_message(message.id)

            for reaction in message.reactions:
                users = [user async for user in reaction.users()]

                if any(str(user) == player.name for user in users):
                    if reaction.emoji == stand_reaction:
                        action = "stand"
                    elif reaction.emoji == hit_reaction:
                        action = "hit"
                    elif reaction.emoji == double_reaction:
                        action = "double"
                    elif reaction.emoji == split_reaction:
                        action = "split"
                    waiting = False
            
        await message.delete()
        return action    




#game = BlackjackGame()
#while True:
#    game.add_player_to_game(load_player_from_file("Igor"))
#    game.add_player_to_game(load_player_from_file("Miłosz"))
#    game.add_player_to_game(load_player_from_file("Patryk"))
#    game.add_player_to_game(load_player_from_file("Kuba"))
#   game.start_game_cli()

