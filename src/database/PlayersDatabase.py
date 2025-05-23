from typing import *
import sqlite3

from database.Database import Database
from utils.Loc import Loc


class PlayerStatistics(NamedTuple):
    current_lose_streak: int
    current_win_streak: int
    highest_lose_streak: int
    highest_win_streak: int
    money_lost: int
    money_won: int

class Item(NamedTuple):
    name: str
    type: str
    picture: str
    object: str


class PlayersDatabase(Database):
    _cursor: sqlite3.Cursor
    
    def __init__(self) -> None:
        super().__init__(name="playersDB")
<<<<<<< HEAD
        self._cursor = sqlite3.connect(f"{Loc.datahub(self.__name)}.db").cursor()

    def player_statistics(self, player: str) -> PlayerStatistics:
        query = """
            SELECT 
                S.current_lose_streak,
                S.current_win_streak,
                S.highest_lose_streak,
                S.highest_win_streak,
                S.money_lost,
                S.money_won
            FROM 
                players P
            JOIN 
                statistics S ON P.id = S.id
            WHERE 
                P.username = ?;
        """
        self._cursor.execute(query, (player,))
        result = self._cursor.fetchone()
        return PlayerStatistics(*result) if result else None
    
    def player_eq(self, player: str) -> List[Item]:
        query = """
            SELECT 
                I.name,
                I.type,
                I.picture,
                I.object
            FROM 
                EQ E
            JOIN 
                ITEMS I ON E.item_id = I.id
            JOIN 
                PLAYERS P ON E.player_id = P.id
            WHERE 
                P.username = ?;
        """
        self._cursor.execute(query, (player,))
        rows = self._cursor.fetchall()
        return [Item(*row) for row in rows]

    

db = PlayersDatabase()
=======
>>>>>>> 3abcbb7 (database: sainity check done)
