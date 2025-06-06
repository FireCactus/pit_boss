from games.cardgames.card_deck import Deck
from games.cardgames.card import Card
from typing import *
import copy


def calculate_blackjack_hand_value(cards: list[Card]) -> int:

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

    def __init__(self, bet:int, cards: list[Card]) -> None:
        self.bet: int = bet
        self.in_play: bool = True
        
        self.cards: list[Card] = cards
        self.value: int = calculate_blackjack_hand_value(self.cards)

    def stand(self) -> None:
        self.in_play = False
    
    def double_down(self) -> None:
        self.bet = self.bet*2
        self.stand()
    
    def get_card_strings(self) -> list[str]:
        '''
        Returns the hand cards in a string format ['A','8','?']
        '''
        card_strings: list[str] = []
        for card in self.cards:
            card_strings.append(card.get_value())
        
        return card_strings
    
    def is_splittable(self) -> bool:
        if len(self.cards) != 2:
            return False
        if calculate_blackjack_hand_value([self.cards[0]]) != calculate_blackjack_hand_value([self.cards[1]]):
            return False
        return True
    
    def is_doubleable(self) -> bool:
        if len(self.cards) != 2:
            return False

        return True

class BlackjackPlayer():

    def __init__(self, name: str, discord_id: int, bet: int) -> None:
        self.name:str = name
        self.discord_id: int = discord_id
        self.initial_bet: int = bet
        self.hands: list[BlackJackHand] = [BlackJackHand(bet,[])]
    
    def split_hand(self, hand_pos: int) -> None:
        original_hand: BlackJackHand = self.hands[hand_pos]
        
        new_hand: BlackJackHand = BlackJackHand(original_hand.bet, [original_hand.cards.pop(-1)])
        original_hand.value = calculate_blackjack_hand_value(original_hand.cards)

        self.hands.append(new_hand)

class BlackjackGame:
    _dealer_draws_to: int = 17
    _shoe_size: int = 6

    _payout_table: Dict[str, float] = {
        "normal_win": 2,
        "blackjack": 2.5
        }

    def __init__(self, player_list: list[BlackjackPlayer]):

        self.players: list[BlackjackPlayer] = player_list
        self.shoe: Deck = self.__construct_deck()

        self.dealer_cards: list[Card] = []
        self.__deal_initial_cards()
        self.dealer_hand_value = calculate_blackjack_hand_value(self.dealer_cards)

    def __construct_deck(self) -> Deck:

        assert self._shoe_size >= 1

        shoe: Deck = Deck(type="normal")
        if self._shoe_size >= 2:

            for i in range(self._shoe_size - 1):
                shoe.insert(Deck(type="normal").cards)

        shoe.shuffle()
        return shoe
    
    def __deal_initial_cards(self) -> None:

        # give each player a card
        for player in self.players:
            self.hit_player(player)

        # give the dealer a card
        self.draw_dealer_card()

        # give the players their second card
        for player in self.players:
            self.hit_player(player)

        # give the dealer the second card face down
        self.dealer_cards.append(self.shoe.draw_card(face_down=True))

    
    def get_current_hands_in_string_form(self) -> Dict[str,list[list[str]]]:
        hand_dict: Dict[str,list[list[str]]] = {'Dealer': [[]]}
        
        #dealer hands
        for card in self.dealer_cards:
            hand_dict['Dealer'][0].append(card.get_value())

        #player hands
        for player in self.players:
            for hand in player.hands:
                if player not in hand_dict:
                    hand_dict[player.name] = []
                
                hand_dict[player.name].append(hand.get_card_strings())
            
        return hand_dict

    def stand_player(self, player: BlackjackPlayer) -> None:
        for hand in player.hands:
            if hand.in_play:
                hand.stand()
                return None
    
    def hit_player(self, player: BlackjackPlayer) -> None:
        for hand in player.hands:
            if hand.in_play == False:
                continue
            hand.cards.append(self.shoe.draw_card(face_down=False))
            hand.value = calculate_blackjack_hand_value(hand.cards)
            
            if hand.value >= 21:
                hand.stand()
            return None
                
    def double_player(self, player: BlackjackPlayer) -> None:
        for hand in player.hands:
            if hand.in_play == False:
                continue
            hand.cards.append(self.shoe.draw_card(face_down=True))
            hand.value = calculate_blackjack_hand_value(hand.cards)
            hand.double_down()
            return None
    
    def split_player(self, player: BlackjackPlayer) -> None:
        for i, hand in enumerate(player.hands):
            if hand.in_play == False:
                continue
            player.split_hand(i)
            return None
    
    def reveal_player_cards(self, player: BlackjackPlayer) -> None:
        for hand in player.hands:
            for card in hand.cards:
                if card.face_down:
                    card.turn_over()
            hand.value = calculate_blackjack_hand_value(hand.cards)
            

    def reveal_dealer_card(self) -> None:
        self.dealer_cards[1].turn_over()
        self.dealer_hand_value = calculate_blackjack_hand_value(self.dealer_cards)
    
    def draw_dealer_card(self) -> None:
        self.dealer_cards.append(self.shoe.draw_card(face_down=False))
        self.dealer_hand_value = calculate_blackjack_hand_value(self.dealer_cards)
    
    
    def calculate_win_amounts(self) -> Dict[BlackjackPlayer,int]:

        win_dict: Dict[BlackjackPlayer,int] = {}
        for player in self.players:
            win_dict[player] = 0
            for hand in player.hands:
                if hand.value > 21:
                    continue
                
                # natural blackjack 
                if hand.value == 21 and len(hand.cards) == 2 and len(player.hands) == 1:
                    if self.dealer_hand_value == 21: #Push
                        win_dict[player] += hand.bet
                    else: # nat bj payout
                        win_dict[player] += int(hand.bet*self._payout_table['blackjack'])
                
                # if dealer busted or has less than the hand
                elif self.dealer_hand_value > 21 or hand.value > self.dealer_hand_value:
                    win_dict[player] += int(hand.bet*self._payout_table['normal_win'])
                
                # if the hand matches the dealer
                elif self.dealer_hand_value == hand.value:
                    win_dict[player] += hand.bet
                    #normally we would check if the dealer has a 21 to "push"
        
        return win_dict

                

                    

                     

                

                
    



