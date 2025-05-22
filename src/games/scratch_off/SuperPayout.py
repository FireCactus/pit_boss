from games.scratch_off.ScratchOffTicket import (
    ScratchOffTicket,
    TicketPayoutRank,
    ScratchOffField,
)
import random

"""
Basic scratch off ticket with the structure:
------------------------------------
|  Winning number:     [a]         |
|  [] [] [] [] [] [] [] [] [] []   |
|  [] [] [] [] [] [] [] [] [] []   |
------------------------------------
"""


class SuperPayout(ScratchOffTicket):
    _field_quantity = 20
    _price = 10
    _name = "Super Payout"
    _ranks = (
        TicketPayoutRank(rank=5, win_amount=0, probability=0.4),
        TicketPayoutRank(rank=4, win_amount=5, probability=0.4),
        TicketPayoutRank(rank=3, win_amount=10, probability=0.1),
        TicketPayoutRank(rank=2, win_amount=50, probability=0.08),
        TicketPayoutRank(rank=1, win_amount=100, probability=0.02),
    )

    def __init__(self):
        super().__init__()
        self._fields = self._generate_fields()

    def _generate_fields(self) -> list[ScratchOffField]:

        fields = []

        self._winning_num = random.randint(1, 31)
        if self._rank.win_amount != 0:
            field = ScratchOffField(str(self._winning_num), self._rank.win_amount)
        else:
            rand_rank = random.choice(self._ranks)
            win_amount = rand_rank.win_amount
            if win_amount == 0:
                win_amount = 5

            field = ScratchOffField(str(self._winning_num + 1), 5)
        fields.append(field)

        for i in range(self._field_quantity - 2):
            rand_rank = random.choice(self._ranks)
            win_amount = rand_rank.win_amount
            if win_amount == 0:
                win_amount = 5

            number = random.randint(1, 31)
            if number == self._winning_num:
                number += 1

            field = ScratchOffField(str(number), win_amount)
            fields.append(field)

        random.shuffle(fields)
        return fields
