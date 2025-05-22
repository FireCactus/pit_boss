from games.cardgames.card_deck import Deck
from games.cardgames.card import Card
from games import game_player as g_player

import math
import time
import discord
import asyncio

stand_reaction = "❌"
hit_reaction = "👆"
split_reaction = "↔️"
double_reaction = "🔥"

DECKS_IN_PLAY = 6  # how many decks in the shoe
PLAYER_STARTER_MONEY = 100

PAYOUT_TABLE = {"normal_win": 2, "draw": 1, "blackjack": 2.5}

delete_after_seconds = 60


def calculate_blackjack_hand_value(cards):

    try:
        cards = cards["cards"]
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
            aces += 1  # save aces for later as we need to know whether they will be a 1 or 11

        elif value in ["J", "Q", "K"]:
            total_value += 10
        else:
            total_value += int(value)

    for _ in range(aces):
        if total_value > 21:
            total_value -= 10  # change the ace to a 1 if the count is above 21

    return total_value


class BlackjackGame:
    def __init__(self, shoe_size=6, min_bet=25, max_bet=1000, max_players=10):
        self.players = []
        self.shoe = self.construct_deck(shoe_size)  # Deck object

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
            raise ValueError(
                "Not enough room at the table!\n the table can only fit {self.max_players} players"
            )

        if type(player) is g_player.GamePlayer:
            if player.money < self.min_bet:
                raise ValueError(
                    f"Player doesnt have enough money to play! \n minimal bet is {self.min_bet}, player has {player.money}"
                )
            if player not in self.players:
                self.players.append(player)
        else:
            raise ValueError(f"player is not BlackjackPlayer but {type(player)}")

    def remove_player(self, player):
        if player not in self.players:
            return

        self.players.remove(player)

    def play_dealer(self):
        Dealer_stop = 17

        self.dealer_cards[1].face_down = False  # turn over the face down card
        self.print_table(end=True)

        while calculate_blackjack_hand_value(self.dealer_cards) < Dealer_stop:
            time.sleep(1)
            self.dealer_cards.append(self.shoe.draw_card(face_down=False))
            self.print_table(end=True)

    def deal_initial_cards(self, player_bets):

        # give each player a card
        for player in self.players:
            card = self.shoe.draw_card(face_down=False)

            player.hands = []  # clear player hands
            hand = {"bet": player_bets[player.name], "cards": [card]}
            player.hands.append(hand)

        # give the dealer a card
        card = self.shoe.draw_card(face_down=False)
        self.dealer_cards.append(card)

        # give the players their second card
        for player in self.players:
            card = self.shoe.draw_card(face_down=False)

            player.hands[0]["cards"].append(card)

        # give the dealer the second card face down
        self.dealer_cards.append(self.shoe.draw_card(face_down=True))

    async def play_dealer_discord(self, ctx):
        Dealer_stop = 17

        self.dealer_cards[1].face_down = False  # turn over the face down card
        table = await self.send_bj_table_to_discord(ctx)
        await asyncio.sleep(1)

        while calculate_blackjack_hand_value(self.dealer_cards) < Dealer_stop:
            await table.delete()

            await asyncio.sleep(1)

            self.dealer_cards.append(self.shoe.draw_card(face_down=False))
            table = await self.send_bj_table_to_discord(ctx)

        for player in self.players:
            for hand in player.hands:
                for card in hand["cards"]:
                    if card.face_down == True:
                        await asyncio.sleep(1)
                        await table.delete()
                        card.face_down = False
                        table = await self.send_bj_table_to_discord(ctx)

    async def start_game_discord(self, ctx, player_bets):

        # remove money from players
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
                    payout = math.floor(
                        player.hands[0]["bet"] * PAYOUT_TABLE["blackjack"]
                    )
                    await ctx.send(
                        f"{player.name} got a blackjack winning {payout}!",
                        delete_after=delete_after_seconds,
                    )
                    player.money += payout
                    playing_players.remove(player)

        ##################### ULTIMATE FIX FOR BUG
        for player in playing_players:
            for hand in player.hands:
                for card in hand["cards"]:
                    card.face_down = False
        self.dealer_cards[0].face_down = False
        ############################################

        # play with each player
        for player in playing_players:

            for i, hand in enumerate(player.hands):
                decision = ""

                while True:
                    table = await self.send_bj_table_to_discord(ctx)
                    decision = await self.ask_user_for_choice_discord(
                        ctx, player, player.hands[i], player.hands[i]["bet"]
                    )
                    await table.delete()

                    if decision == "hit":
                        player.hands[i]["cards"].append(
                            self.shoe.draw_card(face_down=False)
                        )

                        if calculate_blackjack_hand_value(player.hands[i]) >= 21:
                            break

                    elif decision == "stand":
                        break

                    elif decision == "double":
                        player.money -= player.hands[i]["bet"]
                        player.hands[i]["bet"] = player.hands[i]["bet"] * 2
                        player.hands[i]["cards"].append(
                            self.shoe.draw_card(face_down=True)
                        )
                        break

                    elif decision == "split":
                        player.money -= player.hands[i]["bet"]
                        split_card = player.hands[i]["cards"].pop()
                        hand = {"bet": player.hands[i]["bet"], "cards": [split_card]}
                        player.hands.append(hand)

        # play with the dealer
        await self.play_dealer_discord(ctx)

        # check any payouts:
        await ctx.send(
            "------------------------------------------------------------",
            delete_after=delete_after_seconds,
        )
        dealer_total = calculate_blackjack_hand_value(self.dealer_cards)
        if dealer_total > 21:
            for player in playing_players:
                for hand in player.hands:
                    if calculate_blackjack_hand_value(hand) <= 21:
                        payout = math.floor(hand["bet"] * PAYOUT_TABLE["normal_win"])
                        await ctx.send(f"   {player.name} Wins {payout}")
                        player.money += payout
        else:
            for player in playing_players:
                for hand in player.hands:
                    hand_value = calculate_blackjack_hand_value(hand)

                    if hand_value > 21:
                        await ctx.send(
                            f"   {player.name} Loses {hand['bet']}",
                        )
                        continue

                    if hand_value > dealer_total:
                        payout = math.floor(hand["bet"] * PAYOUT_TABLE["normal_win"])
                        await ctx.send(f"   {player.name} Wins {payout}")
                        player.money += payout

                    elif hand_value == dealer_total:
                        payout = math.floor(hand["bet"] * PAYOUT_TABLE["draw"])
                        await ctx.send(
                            f"   {player.name} matched the dealer. draw payout: {payout}"
                        )
                        player.money += payout

                    elif hand_value < dealer_total:
                        await ctx.send(f"   {player.name} Loses {hand['bet']}")

        string = "---------------------Current balance------------------------: \n"
        for player in self.players:
            string += f"   {player.name} - {player.money}\n"

        await ctx.send(string, delete_after=delete_after_seconds)

        # save players to file:
        for player in self.players:
            g_player.save_player_to_file(player)

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
                for card in hand["cards"]:
                    if card.face_down == False:
                        value = card.get_value()
                        color = card.get_color_emoji()
                        string += f"{value}{color}  "
                    else:
                        string += "[?]  "

                string += f"-  ({calculate_blackjack_hand_value(hand)})\n"

        message = await ctx.send(string, delete_after=delete_after_seconds)
        return message

    async def ask_user_for_choice_discord(self, ctx, player, hand, bet):

        timeout = 30  # if after 30s no choice is made, stand for the player

        message = await ctx.send(
            f"What do you want to do {player.name}?\nCurrent hand value is {calculate_blackjack_hand_value(hand)}"
        )
        await message.add_reaction(stand_reaction)
        await message.add_reaction(hit_reaction)

        if player.money >= bet:
            hand = hand["cards"]
            if len(hand) == 2:
                if hand[0].get_value() == hand[1].get_value():
                    await message.add_reaction(split_reaction)
                elif hand[0].get_value() in ["J", "Q", "K", "10"] and hand[
                    1
                ].get_value() in ["J", "Q", "K", "10"]:
                    await message.add_reaction(split_reaction)

            if len(hand) == 2:
                await message.add_reaction(double_reaction)

        start_time = time.time()
        waiting = True
        action = "stand"
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
