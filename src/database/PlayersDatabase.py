from typing import *
import sqlite3
import datetime

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
        self._cursor = sqlite3.connect(f"{Loc.datahub(self._name)}.db").cursor()

    def player_statistics(self, player: str) -> Optional[PlayerStatistics]:
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
    
    def get_player_balance(self, player: str) -> int:
        query = """
            SELECT 
                balance
            FROM 
                players
            WHERE 
                username = ?;
        """
        self._cursor.execute(query, (player,))
        result = self._cursor.fetchone()
        return result
    
    def update_player_balance(self, player: str, amount: int) -> None:
        query = """
            UPDATE players
            SET balance = balance + ?
            WHERE username = ?;
        """
        self._cursor.execute(query, (amount, player))
        self._connection.commit()

    def add_new_player(self, player: str):


        query = """
            INSERT INTO PLAYERS (username, balance, received_daily, exp, title, last_interaction_time)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        self._cursor.execute(query, (
            player,
            500,
            False,
            0,
            "xyz",
            datetime.now().isoformat()
        ))
        self._connection.commit()

db = PlayersDatabase()

