from typing import *
from enum import StrEnum

from games.ChallengeGame import ChallengeGame

class ConnectFourColor(StrEnum):
    YELLOW = "🟡"
    RED = "🔴"

class ConnectFourToken(NamedTuple):
    color: ConnectFourColor 

class ConnectFourBoard(ChallengeGame):
    row_amount: int = 6
    column_amount: int = 7

    in_a_row_to_win: int = 4

    fields: list[list[Optional[ConnectFourToken]]]
    
    def __init__(self):
       self.fields = [[None for _ in range(self.column_amount)] for _ in range(self.row_amount)]


    def insert_token_into_column(self, column_id: int, token: ConnectFourToken) -> None:
        '''
        drops a token into the given column (columns start at 1)
        '''
        assert column_id <= self.column_amount, f"Invalid column id! column needs to be between 1 and {self.column_amount}"
        assert self.fields[0][column_id-1] == None, "This column is full! Cannot insert token"

        current_depth: int = 0
        
        #'drop' token row by row until it's at the bottom
        while current_depth < self.row_amount:

            # if there isnt a token below, drop down
            if self.fields[current_depth][column_id-1] == None:
                current_depth += 1
            else:
                break
                
    
        #reached the end, assign token to field
        self.fields[current_depth-1][column_id-1] = token
        return None
    

    def check_for_wins(self) -> Optional[ConnectFourColor]:
        def check_direction(start_row: int, start_col: int, d_row: int, d_col: int) -> Optional[ConnectFourColor]:
            token = self.fields[start_row][start_col]
            if token is None:
                return None
            color = token.color

            for i in range(1, self.in_a_row_to_win):
                r = start_row + d_row * i
                c = start_col + d_col * i
                if not (0 <= r < self.row_amount and 0 <= c < self.column_amount):
                    return None
                next_token = self.fields[r][c]
                if next_token is None or next_token.color != color:
                    return None
            return color

        for row in range(self.row_amount):
            for col in range(self.column_amount):
                for d_row, d_col in [(0, 1), (1, 0), (1, 1), (1, -1)]:  # right, down, diag-down-right, diag-down-left
                    winner = check_direction(row, col, d_row, d_col)
                    if winner:
                        return winner
        return None

    def get_vacant_columns(self) -> list[int]:
        vacant: list[int] = []
        for i in range(1, self.column_amount+1):
            # check the top most field of all columns
            if self.fields[0][i-1] == None:
                vacant.append(i)
        return vacant


    def get_fields_as_emoji_string(self) -> str:
        string: str = "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n"
        for row in self.fields:
            for token in row:
                string += f'{token.color}' if token!=None else '⚫'
            string += "\n"
        string += "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣"
        return string

        
    

