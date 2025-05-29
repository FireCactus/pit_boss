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

    
    def get_player_balance(self, discord_id: int) -> int:
        query: str= """
            SELECT 
                balance
            FROM 
                players
            WHERE 
                discord_id = ?;
        """
        self._cursor.execute(query, (discord_id,))
        result = self._cursor.fetchone()[0]
        return result
    
    def update_player_balance(self, discord_id: int, amount: int) -> None:
        query: str= """
            UPDATE players
            SET balance = balance + ?
            WHERE discord_id = ?;
        """
        self._cursor.execute(query, (amount, discord_id))
        self._cursor.connection.commit()

    def check_if_player_exists(self, discord_id:int) -> bool:
        query: str= """
            SELECT 
                discord_id
            FROM 
                players
        """
        self._cursor.execute(query)
        result: list[str] = self._cursor.fetchall()
        strings_list = [item[0] for item in result]
        
        if player in strings_list:
            return True
       
        return False
    

    def add_new_player(self, discord_id: int, display_name:str) -> None:



        query: str= """
            INSERT INTO PLAYERS (discord_id, display_name, balance, received_daily, exp, title, last_interaction_time, bet)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        self._cursor.execute(query, (
            discord_id,
            display_name,
            self._welcome_money,
            False,
            0,
            self._starting_gambler_title,
            datetime.datetime.now().isoformat(),
            25
        ))
        self._cursor.connection.commit()
    
    def get_player_bet(self, discord_id: int) -> int:
        query: str = """
            SELECT 
                bet
            FROM 
                players
            WHERE 
                discord_id = ?;
        """
        self._cursor.execute(query, (discord_id,))
        result: int = self._cursor.fetchone()[0]
        return result

    def change_player_bet(self, discord_id: int, amount: int) -> None:
        query: str= """
            UPDATE players
            SET bet = ?
            WHERE discord_id = ?;
        """
        self._cursor.execute(query, (amount, discord_id))
        self._cursor.connection.commit()
    
    def get_all_players(self) -> list[str]:
        query: str= """
            SELECT 
                discord_id
            FROM 
                players
        """
        self._cursor.execute(query)
        result: list[str] = self._cursor.fetchall()
        strings_list = [item[0] for item in result]
       
        return strings_list
    
    def check_if_player_received_daily(self, discord_id: int) -> bool:
        query: str= """
            SELECT 
                received_daily  
            FROM 
                players
            WHERE discord_id = ?
        """
        self._cursor.execute(query, (discord_id,))
        result: str = self._cursor.fetchone()[0]
       
        return bool(result)
    
    def change_player_received_daily(self, discord_id: int, value: bool) -> None:
        query: str= """
            UPDATE players
            SET received_daily = ?
            WHERE discord_id = ?;
        """

        self._cursor.execute(query, (value, discord_id))
        self._cursor.connection.commit()

    def save_item_to_player_inventory(self, discord_id: int, pickle_path: str) -> None:
        query: str= """
        INSERT INTO items
        (object)
        VALUES (?);

        INSERT INTO eq
        (player_discord_id, item_id)
        VALUES (?,last_insert_rowid());
        """

        self._cursor.execute(query, (pickle_path, discord_id))
        self._cursor.connection.commit()

    def delete_item_from_player_inventory(self, pickle_path: str) -> None:
        
        query: str= """
        DELETE FROM items
        WHERE object=?;
        """

        self._cursor.execute(query, (pickle_path))
        self._cursor.connection.commit()
