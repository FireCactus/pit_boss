import random

from games.scratch_off.ScratchOffTicket import (
    ScratchOffTicket,
    TicketPayoutRank,
    ScratchOffField,
)
from player.Item import ItemRepresentation
from player.CasualItem import CasualItemUsage


"""
Basic scratch off ticket with the structure:
------------------------------------
|  Winning number:     [a]         |
|  [] [] [] [] [] [] [] [] [] []   |
|  [] [] [] [] [] [] [] [] [] []   |
------------------------------------
"""


class SuperPayout(ScratchOffTicket):
    _price = 10
    _name = "Super Payout scratch off ticket"
    _description = "if a scratched number is same as winning number you win!"
    _representation = ItemRepresentation(emoji="🎟️", picture=None)
    _ranks = (
        TicketPayoutRank(rank=5, win_amount=0, probability=0.4),
        TicketPayoutRank(rank=4, win_amount=5, probability=0.4),
        TicketPayoutRank(rank=3, win_amount=10, probability=0.1),
        TicketPayoutRank(rank=2, win_amount=50, probability=0.08),
        TicketPayoutRank(rank=1, win_amount=100, probability=0.02),
    )

    _fields_per_row = 8
    _row_amount = 2
    _winning_number: int
    
    def __init__(self) -> None:
        super().__init__(self._name, self._description, self._representation)
        self._fields = self._generate_fields()
        

    def _generate_fields(self) -> list[ScratchOffField]:

        fields: list[ScratchOffField] = []

        field_quantity: int = self._fields_per_row * self._row_amount        
        numbers_left_to_choose: list[int] = list(range(1, 41))

        #generate fields with random numbers
        for _ in range(field_quantity):
            random_number: int = random.choice(numbers_left_to_choose)

            numbers_left_to_choose.remove(random_number)
            fields.append(ScratchOffField(label=str(random_number)))

        #pick the winning number if any:
        if self.get_win_amount() == 0:
            self._winning_number = random.choice(numbers_left_to_choose)
        else:
            self._winning_number = int(random.choice(fields).label)

        return fields

    def use(self) -> CasualItemUsage:
        self._decrement_uses()
        string: str = f"{self.get_description()}\n"
        i: int = -1
        for row in range(self._row_amount):
            for field in range(self._fields_per_row):
                i += 1
                if int(self._fields[i].label) >= 10:
                    string += f" ||{self._fields[i].label}|| "
                else:
                    string += f" ||0{self._fields[i].label}|| "

            string += "\n"
        string += "Super Payout Winning numbers:\n"
        if self.get_win_amount() != 0:
            string += f"if you find ||{self._winning_number}|| you get ||{self.get_win_amount()}||!"
        else:
            string += f"if you find ||{self._winning_number}|| you get ||{random.choice([5,10,50,100])}||!"

        return CasualItemUsage(string)

