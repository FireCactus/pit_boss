from games.cardgames.card import Card, permitted_colors, permitted_values
import random

Normal_suite_values = permitted_values
Normal_suites = permitted_colors


class Deck:
    def __init__(self, type="empty"):
        if type == "normal":

            self.cards = []

            for Suite in Normal_suites:
                for Value in Normal_suite_values:
                    card = Card(Value, Suite)
                    self.cards.append(card)

        elif type == "empty":
            self.cards = []

        else:
            raise ValueError(f"No such deck type as: {type}")

    def draw_card(self, face_down=True):
        card = self.cards.pop(-1)  # pop from top of tdeck
        card.face_down = face_down
        return card

    def size(self):
        return len(self.cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def list_cards(self):
        for card in self.cards:
            val, color = card.get_value_and_color()
            print(f"{val} of {color}")

    def insert(self, cards):
        if isinstance(cards, Card):
            self.cards.append(cards)

        elif isinstance(cards, list):
            for card in cards:
                self.insert(card)
        else:
            raise ValueError(
                f"Invalid object ( {card} ) passed to deck. \n deck.insert accepts only objects of class Card and lists of Cards"
            )
