from games.scratch_off.ScratchOffTicket import ScratchOffTicket, TicketPayoutRank, ScratchOffField
from typing import Optional
import random
import itertools

from player.Item import ItemRepresentation
from player.CasualItem import CasualItemUsage

'''
Basic scratch off ticket with the structure:
-------------------------------------
if X wins you win!
if O loses or draws -> you lose
------------------------------------
'''
class TickTackToeTable:
    def __init__(self, o_moves_first: bool = True) -> None:
        self.fields: list[Optional[str]] = [None] * 9
        self.o_emoji: str = "⭕"
        self.x_emoji: str = "❌"
        
        self.first_to_move: str = self.o_emoji if o_moves_first else self.x_emoji

        self.win_patterns: list[list[int]] = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6],             # diagonals
        ]


    def _check_if_symbol_wins_on_board(self, fields: list[str], symbol: str) -> bool:
        '''
        checks if in the provided fields a given symbol wins by any win pattern
        '''
        for pattern in self.win_patterns:
            if all(fields[i] == symbol for i in pattern):
                return True
        return False

    def generate_draw_table(self) -> None:
        '''
        Generate all possible draw boards and pick one at random
        '''
        other_symbol: str = self.x_emoji if self.first_to_move == self.o_emoji else self.o_emoji
        starter_count: int = 5
        other_count: int = 4

        
        draw_boards: List[List[str]] = []
        # All possible placements of positions for the starter symbol
        for starter_positions in itertools.combinations(range(9), starter_count):
            board: List[Optional[str]] = [None] * 9
            for i in range(9):
                if i in starter_positions:
                    board[i] = self.first_to_move
                else:
                    board[i] = other_symbol

            if not self._check_if_symbol_wins_on_board(board, self.first_to_move): 
                if not self._check_if_symbol_wins_on_board(board, other_symbol):
                    draw_boards.append(board)


        # Pick one at random
        self.fields = random.choice(draw_boards)


    def generate_win_table(self, x_wins: bool = False) -> None:

        self.fields = [None] * 9

        winning_symbol: str = self.x_emoji if x_wins else self.o_emoji
        losing_symbol: str = self.o_emoji if x_wins else self.x_emoji

        for i in random.choice(self.win_patterns):
            self.fields[i] = winning_symbol

        #get field positions that still need to be filled
        remaining_fields: list[int] = [i for i in range(9) if self.fields[i] is None]
            
        x_count: int = self.fields.count(self.x_emoji)
        o_count: int = self.fields.count(self.o_emoji)

        max_x: int = 5 if self.first_to_move==self.x_emoji else 4
        max_o: int = 5 if self.first_to_move==self.o_emoji else 4

        for position in remaining_fields:
            options: list[Optional[str]] = [self.o_emoji, self.x_emoji]
            random.shuffle(options)

            for symbol in options:
                #check if the table can fit another 'O'
                if symbol == self.o_emoji and o_count >= max_o:
                    continue
                #check if the table can fit another 'X'
                if symbol == self.x_emoji and x_count >= max_x:
                    continue

                #if generating an 'X' win board, check that 'O' doesnt win and vice versa
                if symbol == losing_symbol:
                    test_fields: list[Optional[str]] = self.fields[:]
                    test_fields[position] = symbol
                    
                    if self._check_if_symbol_wins_on_board(test_fields, losing_symbol) == True:
                        continue

                #assign the symbol to the board and increment counters
                self.fields[position] = symbol
                if symbol == self.x_emoji:
                    x_count += 1
                elif symbol == self.o_emoji:
                    o_count += 1
                #make sure  only 1 symbol gets assigned per field
                break


class XMarksTheSpot(ScratchOffTicket):
    _price = 30
    _name = "X marks the spot scratch off ticket"
    _description = "If X wins you win!"
    _representation = ItemRepresentation(emoji="🎟️", picture=None)
    _ranks = (
        TicketPayoutRank(rank=3, win_amount=0, probability=0.6),   # O win
        TicketPayoutRank(rank=2, win_amount=32, probability=0.3),  # draw
        TicketPayoutRank(rank=1, win_amount=200, probability=0.1), # X win
        )

    _fields_per_row = 3
    _row_amount = 3

    def __init__(self) -> None:
        super().__init__(self._name, self._description, self._representation)
        self._fields = self._generate_fields()

    def _generate_fields(self) -> list[ScratchOffField]:
        fields: list[ScratchOffField] = []

        table: TickTackToeTable = TickTackToeTable(o_moves_first=True)
        if self._rank.rank == 1:
            table.generate_win_table(x_wins=True)
        elif self._rank.rank == 2:
            table.generate_draw_table()
        elif self._rank.rank == 3:
            table.generate_win_table(x_wins=False)

        for symbol in table.fields:
            fields.append(ScratchOffField(label=symbol))

        return fields

    def use(self) -> CasualItemUsage:
        self._decrement_uses()
        string: str = f"{self.get_description()}\n"
        i: int = -1
        for row in range(self._row_amount):
            for field in range(self._fields_per_row):
                i += 1
                string += f" ||{self._fields[i].label}|| "
            string += "\n"
        string += "X marks the spot Payout table:\n"
        table: TickTackToeTable = TickTackToeTable()
        string += f"{table.x_emoji} Wins -> {self._ranks[2].win_amount}\n"
        string += f"Draw -> {self._ranks[1].win_amount}\n"
        string += f"{table.o_emoji} Wins -> {self._ranks[0].win_amount}\n"

        return CasualItemUsage(string)

  
tick = XMarksTheSpot()
print(tick.use().returned_string)
print(tick.get_win_amount())
print(tick.get_expected_value())