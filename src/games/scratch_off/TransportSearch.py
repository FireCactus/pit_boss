from scratch_off import ScratchOffTicket, TicketPayoutRank, ScratchOffField
import random
'''
Basic scratch off ticket with the structure:
-------------------------------------
    Each pair of three wins!
    [] [] [] [] [] []   [a]- 5
    [] [] [] [] [] []   [b]- 10
    [] [] [] [] [] []   [c]- 50
    [] [] [] [] [] []   [d]- 100
    [] [] [] [] [] []   [e]- 500
    [] [] [] [] [] []
    
------------------------------------
'''

class TransportSearch(ScratchOffTicket):
    _price = 50
    _name = "Transport search"
    _ranks = ( 
        TicketPayoutRank(rank=13, win_amount=0,    probability=0.25), 
        TicketPayoutRank(rank=12, win_amount=5,    probability=0.1),  # 1x5
        TicketPayoutRank(rank=11, win_amount=10,   probability=0.2),  # 2x5
        TicketPayoutRank(rank=10, win_amount=15,   probability=0.1),  # 3x5
        TicketPayoutRank(rank=9,  win_amount=25,   probability=0.15), # 2x10 1x5   
        TicketPayoutRank(rank=8,  win_amount=50,   probability=0.03), # 1x50  
        TicketPayoutRank(rank=7,  win_amount=65,   probability=0.03), # 1x50 1x10 1x5 
        TicketPayoutRank(rank=6,  win_amount=80,   probability=0.025),# 1x50 3x10
        TicketPayoutRank(rank=5,  win_amount=100,  probability=0.015),# 1x100
        TicketPayoutRank(rank=4,  win_amount=150,  probability=0.04), # 1x100 1x50
        TicketPayoutRank(rank=3,  win_amount=300,  probability=0.03), # 3x100
        TicketPayoutRank(rank=2,  win_amount=500,  probability=0.02), # 1x500
        TicketPayoutRank(rank=1,  win_amount=1000, probability=0.01)  # 2x500
        )

    _possible_emojis = [
        "🚗", 
        "🚙",
        "✈️",
        "🚋", 
        "🚜", 
        "🚲",
        "🏍️", 
        "🦽", 
        "🚀",
        "⛵", 
        "🚕", 
        "🚊",
        "🚂", 
        "🛴"
    ]

    _paying_emojis = {
        500: "🚀",
        100: "🚊",
        50: "⛵",
        10: "🚗",
        5: "🚲"
        }

    _fields_per_row = 6
    _row_amount = 6
    _field_quantity=_fields_per_row*_row_amount
    _how_many_fields_to_win = 3

    def __init__(self):
        super().__init__()
        self._fields = self._generate_fields()


    def _generate_fields(self) -> list[ScratchOffField]:
        fields = []
    
        #add the winning emojis first
        remaining_win_to_add = self._rank.win_amount
        while remaining_win_to_add > 0:
            for money, emoji in self._paying_emojis.items():
                if remaining_win_to_add >= money:
                    remaining_win_to_add -= money
                    for _ in range(self._how_many_fields_to_win): 
                        fields.append(ScratchOffField(label=emoji))
                    break
                    
        
        #generate the rest of the emojis
        remaining_fields = (self._fields_per_row * self._row_amount) - len(fields)
        for _ in range(remaining_fields):
            emoji = random.choice(self._possible_emojis)

            if emoji in self._paying_emojis.values():
                #check if we can add that emoji (has to be less than self._how_many_fields_to_win)
                emoji_count = [field.label for field in fields].count(emoji)
                if emoji_count % self._how_many_fields_to_win == self._how_many_fields_to_win -1:
                    self._possible_emojis.remove(emoji)
                    emoji = random.choice(self._possible_emojis)

            fields.append(ScratchOffField(label=emoji))

        #shuffle the list and return
        #random.shuffle(fields)
        return fields