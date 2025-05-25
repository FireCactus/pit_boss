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

    _welcome_money: int = 500
    _starting_gambler_title = "Novice gambler"
    
    def __init__(self) -> None:
        super().__init__(name="playersDB")
        self._cursor = sqlite3.connect(f"{Loc.datahub(self._name)}.db").cursor()

    def player_statistics(self, player: str) -> Optional[PlayerStatistics]:
        query: str= """
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
        result = self._cursor.fetchone()[0]
        return PlayerStatistics(*result) if result else None
    
    def player_eq(self, player: str) -> List[Item]:
        query: str= """
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
        strings_list = [item[0] for item in rows]
        return [Item(*row) for row in strings_list]
    
    def get_player_balance(self, player: str) -> int:
        query: str= """
            SELECT 
                balance
            FROM 
                players
            WHERE 
                username = ?;
        """
        self._cursor.execute(query, (player,))
        result = self._cursor.fetchone()[0]
        return result
    
    def update_player_balance(self, player: str, amount: int) -> None:
        query: str= """
            UPDATE players
            SET balance = balance + ?
            WHERE username = ?;
        """
        self._cursor.execute(query, (amount, player))
        self._cursor.connection.commit()

    def check_if_player_exists(self, player:str) -> bool:
        query: str= """
            SELECT 
                username
            FROM 
                players
        """
        self._cursor.execute(query)
        result: list[str] = self._cursor.fetchall()
        strings_list = [item[0] for item in result]
        
        if player in strings_list:
            return True
       
        return False
    

    def add_new_player(self, player: str) -> None:


        query: str= """
            INSERT INTO PLAYERS (username, balance, received_daily, exp, title, last_interaction_time, bet)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        self._cursor.execute(query, (
            player,
            self._welcome_money,
            False,
            0,
            self._starting_gambler_title,
            datetime.datetime.now().isoformat(),
            25
        ))
        self._cursor.connection.commit()
    
    def get_player_bet(self, player: str) -> int:
        query: str = """
            SELECT 
                bet
            FROM 
                players
            WHERE 
                username = ?;
        """
        self._cursor.execute(query, (player,))
        result: int = self._cursor.fetchone()[0]
        return result

    def change_player_bet(self, player: str, amount: int) -> None:
        query: str= """
            UPDATE players
            SET bet = ?
            WHERE username = ?;
        """
        self._cursor.execute(query, (amount, player))
        self._cursor.connection.commit()
    
    def get_all_players(self) -> list[str]:
        query: str= """
            SELECT 
                username
            FROM 
                players
        """
        self._cursor.execute(query)
        result: list[str] = self._cursor.fetchall()
        strings_list = [item[0] for item in result]
       
        return strings_list
    
    def check_if_player_received_daily(self, player: str) -> bool:
        query: str= """
            SELECT 
                received_daily  
            FROM 
                players
            WHERE username = ?
        """
        self._cursor.execute(query, (player,))
        result: str = self._cursor.fetchone()[0]
       
        return bool(result)
    
    def change_player_received_daily(self, player: str, value: bool) -> None:
        query: str= """
            UPDATE players
            SET received_daily = ?
            WHERE username = ?;
        """

        self._cursor.execute(query, (value, player))
        self._cursor.connection.commit()