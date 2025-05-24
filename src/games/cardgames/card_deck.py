from games.cardgames.card import Card, permitted_colors, permitted_values
import random
from typing import Union

Normal_suite_values: list[str] = permitted_values
Normal_suites: list[str] = permitted_colors


class Deck:
    def __init__(self, type:str ="empty") -> None:
        self.cards: list[Card]
        if type == "normal":

            self.cards = []

            for Suite in Normal_suites:
                for Value in Normal_suite_values:
                    card: Card = Card(Value, Suite)
                    self.cards.append(card)

        elif type == "empty":
            self.cards = []

        else:
            raise ValueError(f"No such deck type as: {type}")

    def draw_card(self, face_down:bool = True) -> Card:
        card: Card = self.cards.pop(-1)  # pop from top of tdeck
        card.face_down = face_down
        return card

    def size(self) -> int:
        return len(self.cards)

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def insert(self, cards: Union[list[Card], Card]) -> None:
        if isinstance(cards, Card):
            self.cards.append(cards)

        elif isinstance(cards, list):
            for card in cards:
                self.insert(card)
        else:
            raise ValueError(f"Invalid object ( {cards} ) passed to deck. \n deck.insert accepts only objects of class Card and lists of Cards")
