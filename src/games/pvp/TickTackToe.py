from typing import *
from enum import StrEnum

from games.ChallengeGame import ChallengeGame

field_emoji_dict: Dict[int,str]={
    1 : "1️⃣",
    2 : "2️⃣",
    3 : "3️⃣",
    4 : "4️⃣",
    5 : "5️⃣",
    6 : "6️⃣",
    7 : "7️⃣",
    8 : "8️⃣",
    9 : "9️⃣"
}

class TickTackToeSymbol(StrEnum):
    CROSS = "❌"
    NOUGHT = "⭕"


class TickTackToeBoard(ChallengeGame):
    row_amount: int = 3
    column_amount: int = 3

    fields: list[Optional[TickTackToeSymbol]]
    
    def __init__(self):
       self.fields = [None]*(self.column_amount*self.row_amount)


    def place_symbol_into_field(self, field: int, symbol: TickTackToeSymbol) -> None:
        assert field >= 1 and field <= 9, "Invalid field chosen!, must be between 1 and 9"
        assert self.fields[field-1] == None, "The designated field is already occupied, pick an empty field"
        
        self.fields[field-1] = symbol    

    def _check_if_symbol_wins_on_board(self, symbol: str) -> bool:
        '''
        checks if in the provided fields a given symbol wins by any win pattern
        '''
        
        win_patterns: list[list[int]] = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6],             # diagonals
        ]
       
        for pattern in win_patterns:
            if all(self.fields[i] == symbol for i in pattern):
                return True
        return False


    def get_vacant_fields(self) -> list[int]:
        vacant: list[int] = []
        for i in range(1, (self.column_amount*self.row_amount)+1):
            # check the top most field of all columns
            if self.fields[i-1] == None:
                vacant.append(i)
        return vacant


    def get_fields_as_emoji_string(self) -> str:
        string: str = ""
        for i, symbol in enumerate(self.fields):
            string += f'{symbol}' if symbol!=None else field_emoji_dict[i+1]
            if (i+1) % self.row_amount == 0:
                string += "\n"
        return string
