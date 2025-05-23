from scratch_off import ScratchOffTicket, TicketPayoutRank, ScratchOffField
from typing import Optional
import random
'''
Basic scratch off ticket with the structure:
-------------------------------------
if all 3 characters match - you win
 [a]- 15       []  []  [] 
 [b] - 20      []  []  [] 
 [c] - 35      []  []  [] 
 [d] - 50      []  []  [] 
 [e] - 200     []  []  [] 
 [f] - 1000    []  []  []
    
------------------------------------
'''

class EmojiLines(ScratchOffTicket):
    _price = 25
    _name = "Emoji lines"
    _description = "if all 3 emojis are the same in a line you win!"
    _ranks = (
        TicketPayoutRank(rank=7, win_amount=0, probability=0.3),
        TicketPayoutRank(rank=6, win_amount=15, probability=0.4),
        TicketPayoutRank(rank=5, win_amount=20, probability=0.15),
        TicketPayoutRank(rank=4, win_amount=35, probability=0.08),
        TicketPayoutRank(rank=3, win_amount=50, probability=0.05),
        TicketPayoutRank(rank=2, win_amount=200, probability=0.012),
        TicketPayoutRank(rank=1, win_amount=1000, probability=0.008)
        )
    _possible_emojis = ["⚠️", "📅", "😜", "😻", "☠️", "🏆", "🎀", "👑", "🎵", "🍎", "☢️"]
    _paying_emojis = {
        _ranks[1].win_amount: "⚠️",
        _ranks[2].win_amount: "🌋",
        _ranks[3].win_amount: "😜",
        _ranks[4].win_amount: "😻",
        _ranks[5].win_amount: "☠️",
        _ranks[6].win_amount: "🏆"
        }
    _fields_per_row = 3
    _row_amount = 6


    def __init__(self) -> None:
        super().__init__()
        self._fields = self._generate_fields()


    def _generate_fields(self) -> list[ScratchOffField]:
        fields: list[ScratchOffField] = []

        winning_row: Optional[int] = None
        if self._rank.win_amount != 0:
            winning_row = random.randint(0,self._row_amount-1)

        i: int = 0
        for row in range(self._row_amount):
            for column in range(self._fields_per_row):
                emoji: str
                if row == winning_row:
                    emoji = self._paying_emojis[self._rank.win_amount]
                else:
                    emoji = random.choice(self._possible_emojis)

                if row != winning_row and column == 2:
                    if emoji == fields[i-1].label and emoji == fields[i-2].label:
                        # if not winning row and last emoji in row, if chosen emoji is same as two previous ones, change it                    
                        safe_emoji_set: list[str] = self._possible_emojis.copy()
                        safe_emoji_set.remove(emoji) #create a new emoji set without the one we have chosen

                        emoji = random.choice(safe_emoji_set)

                fields.append(ScratchOffField(emoji))
                i += 1
                
        return fields


  
