from typing import *

from database.Database import Database
from utils.Loc import Loc

class PlayersDatabase(Database):

    def __init__(self) -> None:
        super().__init__(name="playersDB")