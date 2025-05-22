from EmojiLines import EmojiLines
from scratch_off import TicketPayoutRank, ScratchOffField

'''
Basic scratch off ticket with the structure:
-------------------------------------
if all 3 characters match - you win
 [a]- 15       []  []  []  [] 
 [b] - 20      []  []  []  []
 [c] - 35      []  []  []  []
 [d] - 50      []  []  []  []
 [e] - 200     
 [f] - 1000    
------------------------------------
'''

class DiamondRush(EmojiLines):
    _price = 55
    _name = "Diamond rush"
    _ranks = (
        TicketPayoutRank(rank=8, win_amount=0, probability=0.15),
        TicketPayoutRank(rank=7, win_amount=10, probability=0.15),
        TicketPayoutRank(rank=6, win_amount=25, probability=0.4),
        TicketPayoutRank(rank=5, win_amount=30, probability=0.15),
        TicketPayoutRank(rank=4, win_amount=100, probability=0.08),
        TicketPayoutRank(rank=3, win_amount=250, probability=0.05),
        TicketPayoutRank(rank=2, win_amount=500, probability=0.012),
        TicketPayoutRank(rank=1, win_amount=1500, probability=0.008)
        )
    _possible_emojis = ["💎","💠","💍", "💰", "💸","🛢️", "🪙","💵"]
    _paying_emojis = {
        _ranks[1].win_amount: "🪙",
        _ranks[2].win_amount: "💵",
        _ranks[3].win_amount: "💸",
        _ranks[4].win_amount: "💰",
        _ranks[5].win_amount: "💠",
        _ranks[6].win_amount: "💍",
        _ranks[7].win_amount: "💎"
        }
    _fields_per_row = 4
    _row_amount = 4
    _field_quantity=_fields_per_row*_row_amount

    def __init__(self):
        super().__init__()
        self._fields = self._generate_fields()
