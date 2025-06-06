from abc import ABC, abstractmethod
from typing import NamedTuple, Optional
from statistics import mean 
import random

from player.Item import Item, ItemRepresentation, DepletedItem
from player.CasualItem import CasualItem, CasualItemUsage


class TicketPayoutRank(NamedTuple):
    rank: int 
    win_amount: int
    probability: float

class ScratchOffField(NamedTuple):
    label: str
    
class ScratchOffTicket(CasualItem, ABC):

    _fields_per_row: int
    _row_amount: int

    _price: int
    _name: str
    _description: str
    _representation: ItemRepresentation
    
    _ranks: tuple[TicketPayoutRank]
    _rank: TicketPayoutRank
    _fields: list[ScratchOffField]

    #used for emoji scratch offs
    _possible_emojis: Optional[list[str]]
    _paying_emojis: Optional[dict[int,str]]


    def __init__(self, name: str, description:str, representation: ItemRepresentation) -> None:
        super().__init__(name, description, representation)
        self.check_if_ticket_probabilites_are_valid()
        self._rank = self._decide_ticket_rank()

        self._field_quantity = self._fields_per_row * self._row_amount
        self._scratched = False

    def get_price(self) -> int:
        return self._price

    def _decide_ticket_rank(self) -> TicketPayoutRank:

        rank_identifier: float = random.random() # 0...1
        current_rank: float = 0
        
        for rank in self._ranks:
            current_rank += rank.probability
            if rank_identifier <= current_rank:
                return rank
        raise ValueError("Rank was not chosen! check ticket rank probabilities!")

    def check_if_ticket_probabilites_are_valid(self) -> None:
        '''
        check if all probabilities add up to 1
        '''
        total: float = 0
        for rank in self._ranks:
            total += rank.probability

        assert total >= 0.9999 and total <= 1.000000002, f"The Ticket probabilities do NOT add up to 1 but {total}"
        # floating point math fix

    def get_expected_value(self) -> float:
        
        total_value: float = 0
        for rank in self._ranks:
            total_value += rank.probability * rank.win_amount
        
        return total_value

    def get_win_amount(self) -> int:
        '''
            Returns the ticket win amount
        '''
        return self._rank.win_amount


    @abstractmethod
    def _generate_fields(self) -> None:
        '''
            generate the fields in the scratcher
        '''      
        pass


    def __repr__(self) -> str:
        string: str = ""
        for i, field in enumerate(self._fields):
            string += f"{field.label} "
        return string

        

