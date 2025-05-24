from games.cardgames.card_deck import Deck
from games.cardgames.card import Card
from typing import Union, Optional
from discord import Message, User
from discord.ext.commands import Context


import math
import time
import discord
import asyncio


def calculate_blackjack_hand_value(cards: Union[list[Card],Card]) -> int:

    if isinstance(cards, Card):
        cards = [cards]

    total_value: int = 0
    aces: int = 0
    for card in cards:
        if card.face_down == True:
            continue

        value: str = card.get_value()
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

class BlackJackHand():

    def __init__(self, bet:int, cards: Optional[list[Card]]=None) -> None:
        self.bet: int = bet
        self.in_play: bool = True
        
        self.cards: list[Card] 
        if cards == None:
            self.cards = []
        else:
            self.cards = cards

    def stand(self) -> None:
        self.in_play = False
    
    def double_down(self) -> None:
        self.bet = self.bet*2
        self.stand()
    
    def is_splittable(self) -> bool:
        if len(self.cards) != 2:
            return False
        if calculate_blackjack_hand_value(self.cards[0]) != calculate_blackjack_hand_value(self.cards[1]):
            return False
        return True
    
    def is_doubleable(self) -> bool:
        if len(self.cards) != 2:
            return False

        return True

class BlackjackPlayer():


    def __init__(self, name: str, bet: int, balance:int) -> None:
        self.name:str = name
        self.initial_bet: int = bet
        self.balance:int = balance # used for determining if the user will have enough for splits and doubles
        self.money_spent_on_actions: int = 0 # how much the users spent on doubling or splitting 
        self.hands: list[BlackJackHand] = [BlackJackHand(bet)]
    
    def split_hand(self, hand_pos: int) -> None:
        original_hand: BlackJackHand = self.hands[hand_pos]
        new_hand: BlackJackHand = BlackJackHand(original_hand.bet, [original_hand.cards.pop(-1)])

        self.hands.append(new_hand)
        


class BlackjackGame:
    _stand_reaction: str = "❌"
    _hit_reaction: str = "👆"
    _split_reaction: str = "↔️"
    _double_reaction: str = "🔥"

    _dealer_draws_to = 17
    _user_decision_timeout = 30

    _payout_table: dict[str, float] = {
        "normal_win": 2,
        "draw": 1,
        "blackjack": 2.5}

    def __init__(self, player_list: list[BlackjackPlayer], shoe_size: int = 6):

        self.players: list[BlackjackPlayer] = player_list
        self.shoe: Deck = self.construct_deck(shoe_size)

        self.dealer_cards: list[Card] = []

    def construct_deck(self, n_decks: int) -> Deck:
        assert n_decks >= 1

        shoe: Deck = Deck(type="normal")
        cards: list[Card] = shoe.cards.copy()

        if n_decks >= 2:

            for i in range(n_decks - 1):
                shoe.insert(cards)

        shoe.shuffle()
        return shoe


    def deal_initial_cards(self) -> None:

        # give each player a card
        for player in self.players:
            player.hands[0].cards.append(self.shoe.draw_card(face_down=False))

        # give the dealer a card
        self.dealer_cards.append(self.shoe.draw_card(face_down=False))

        # give the players their second card
        for player in self.players:
            player.hands[0].cards.append(self.shoe.draw_card(face_down=False))

        # give the dealer the second card face down
        self.dealer_cards.append(self.shoe.draw_card(face_down=True))

    async def play_dealer_discord(self, ctx: Context, blackjack_table: Message) -> None:

        self.dealer_cards[1].face_down = False  # turn over the face down card
        await self.send_bj_table_to_discord(ctx, blackjack_table)
        await asyncio.sleep(1)

        while calculate_blackjack_hand_value(self.dealer_cards) < self._dealer_draws_to:
            await asyncio.sleep(1)

            self.dealer_cards.append(self.shoe.draw_card(face_down=False))
            await self.send_bj_table_to_discord(ctx, blackjack_table)

        for player in self.players:
            for hand in player.hands:
                for card in hand.cards:
                    if card.face_down == True:
                        await asyncio.sleep(1)
                        card.face_down = False
                        await self.send_bj_table_to_discord(ctx, blackjack_table)

    async def start(self, ctx: Context) -> dict[str, int]:
        
        # initial dealing ---------
        self.deal_initial_cards()

        # check if anyone got a blackjack
        for player in self.players:
                total = calculate_blackjack_hand_value(player.hands[0].cards)
                if total == 21:
                    player.hands[0].in_play = False
                    await ctx.send(f"{player.name} got a blackjack!")

        #display the table for the first time
        blackjack_table: Message = await self.send_bj_table_to_discord(ctx)

        # play with each player
        for player in self.players:
            for i, hand in enumerate(player.hands):

                decision: str
                while hand.in_play:
                    table = await self.send_bj_table_to_discord(ctx,blackjack_table)
                    decision = await self.ask_user_for_choice_discord(ctx, player, i)

                    if decision == "hit":
                        player.hands[i].cards.append(self.shoe.draw_card(face_down=False))

                    elif decision == "stand":
                        player.hands[i].stand()

                    elif decision == "double":
                        player.balance -= player.hands[i].bet
                        player.money_spent_on_actions += player.hands[i].bet

                        player.hands[i].cards.append(self.shoe.draw_card(face_down=True))
                        player.hands[i].double_down()   

                    elif decision == "split":
                        player.split_hand(i)
                        player.balance -= player.hands[i].bet
                        player.money_spent_on_actions += player.hands[i].bet
                    
                    if calculate_blackjack_hand_value(player.hands[i].cards) >= 21:
                        player.hands[i].in_play = False


        # play with the dealer
        await self.play_dealer_discord(ctx, blackjack_table)

        # check any payouts:
        winners_table: dict[str,int] = {}

        for player in self.players:
            winners_table[player.name] =- player.money_spent_on_actions
        

        dealer_total = calculate_blackjack_hand_value(self.dealer_cards)
        if dealer_total > 21:
            for player in self.players:
                for hand in player.hands:
                    if calculate_blackjack_hand_value(hand.cards) <= 21:
                        payout = math.floor(hand.bet * self._payout_table["normal_win"])
                        winners_table[player.name] += payout

        else:
            for player in self.players:
                for hand in player.hands:
                    hand_value = calculate_blackjack_hand_value(hand.cards)

                    if hand_value > 21:
                        continue

                    if hand_value > dealer_total:
                        payout = math.floor(hand.bet * self._payout_table["normal_win"])
                        winners_table[player.name] += payout

                    elif hand_value == dealer_total:
                        payout = math.floor(hand.bet * self._payout_table["draw"])
                        winners_table[player.name] += payout

        return winners_table
    

    async def send_bj_table_to_discord(self, ctx: Context, edit_message: Optional[Message] = None) -> Message:
        string: str = "-----------------------------------------\n"
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
                for card in hand.cards:
                    if card.face_down == False:
                        value = card.get_value()
                        color = card.get_color_emoji()
                        string += f"{value}{color}  "
                    else:
                        string += "[?]  "

                string += f"-  ({calculate_blackjack_hand_value(hand.cards)})\n"

        message: Message
        if edit_message == None:
            message = await ctx.send(string)
        else:
            message = await edit_message.edit(content=string)
        
        return message

    async def ask_user_for_choice_discord(self, ctx: Context, player: BlackjackPlayer, hand_number: int) -> str:

        message: Message = await ctx.send(
            f"What do you want to do {player.name}?\nCurrent hand value is {calculate_blackjack_hand_value(player.hands[hand_number].cards)}"
        )

        await message.add_reaction(self._stand_reaction)
        await message.add_reaction(self._hit_reaction)

        hand: BlackJackHand = player.hands[hand_number]
        if player.balance >= hand.bet *2:
            if hand.is_doubleable():
                await message.add_reaction(self._double_reaction)
            if hand.is_splittable():
                await message.add_reaction(self._split_reaction)
    
        start_time: float = time.time()
        waiting: bool = True
        action: str = "stand"

        while waiting and time.time() - start_time <= self._user_decision_timeout:
            await asyncio.sleep(1.1)
            message = await ctx.channel.fetch_message(message.id)

            for reaction in message.reactions:
                users:list[str] = [str(user) async for user in reaction.users()]

                if any(str(user) == player.name for user in users):
                    if reaction.emoji == self._stand_reaction:
                        action = "stand"
                    elif reaction.emoji == self._hit_reaction:
                        action = "hit"
                    elif reaction.emoji == self._double_reaction:
                        action = "double"
                    elif reaction.emoji == self._split_reaction:
                        action = "split"
                    waiting = False

        await message.delete()
        return action