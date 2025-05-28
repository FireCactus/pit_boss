from typing import *
from abc import ABC, abstractmethod


# all interaction happens outside of this class
# this class is only used to handle game frames.

#move all message functions to a utils class

class Game(ABC):
    _payout_table: Dict[str,float] # how much to pay out for each scenario


