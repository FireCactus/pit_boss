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

    _fields_per_row = 10
    _row_amount = 2

    def __init__(self) -> None:
        super().__init__(self._name, self._description, self._representation)
        self._fields = self._generate_fields()

    def _generate_fields(self) -> list[ScratchOffField]:

        fields: list[ScratchOffField] = []
        field: ScratchOffField 

        self._winning_num = random.randint(1, 31)
        if self._rank.win_amount != 0:
            field = ScratchOffField(str(self._winning_num), self._rank.win_amount)
        else:
            rand_rank: TicketPayoutRank = random.choice(self._ranks)
            win_amount: int = rand_rank.win_amount
            if win_amount == 0:
                win_amount = 5

            field = ScratchOffField(str(self._winning_num + 1), 5)
        fields.append(field)

        for _ in range((self._fields_per_row*self._fields_per_row) - 2):
            rand_rank = random.choice(self._ranks)
            win_amount = rand_rank.win_amount
            if win_amount == 0:
                win_amount = 5

            number: int = random.randint(1, 31)
            if number == self._winning_num:
                number += 1

            field = ScratchOffField(str(number), win_amount)
            fields.append(field)

        random.shuffle(fields)
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
        string += "Super Payout Payout table:\n"
        string += f"if you find ||{self._winning_num}|| you get ||{self.get_win_amount()}||!"

        return CasualItemUsage(string)
