from typing import *
import sqlite3
import datetime

from database.Database import Database
from utils.Loc import Loc
from utils.Files import Files 


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
    _shop_discord_id: int = 1
    
    _welcome_money: int = 500
    _starting_gambler_title = "Novice gambler"
    
    def __init__(self) -> None:
        super().__init__(name="playersDB")

        # Check if the shop user exists and create it if missing (HACK)
        if self.check_if_player_exists(self._shop_discord_id) == False:
            self.add_new_player(self._shop_discord_id, "Shop")

        Files.create_dir_if_not_exist(Loc.datahub("jar"))
    
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
            SELECT discord_id
            FROM players
        """

        self._cursor.execute(query)
        result: list[str] = self._cursor.fetchall()
        strings_list = [item[0] for item in result]
        
        if discord_id in strings_list:
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
        self._connection.commit()
    
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
        self._connection.commit()
    
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
        strings_list.pop(0) # remove the shop user

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
        self._connection.commit()

    def renew_daily_for_all(self) -> None:
        query: str= """
           UPDATE players
           SET received_daily=false;
        """

        self._cursor.execute(query)
        self._connection.commit()


    def save_item_to_player_inventory(self, discord_id: int, pickle_path: str) -> None:

        item_query:str = "INSERT INTO items (object) VALUES (?);"
        self._cursor.execute(item_query, (pickle_path,))

        eq_query = "INSERT INTO eq (player_discord_id, item_id) VALUES (?, ?);"
        self._cursor.execute(eq_query, (discord_id, self._cursor.lastrowid))

        self._connection.commit()

    def delete_item_from_player_inventory(self, pickle_path: str) -> None:
        
        query: str= """DELETE FROM items WHERE object=?;"""

        self._cursor.execute(query, (pickle_path,))
        self._connection.commit()
    
    def get_player_items(self, discord_id: int) -> list[str]:
        query: str= """
        SELECT items.object
        FROM eq
        JOIN items ON eq.item_id = items.id
        WHERE eq.player_discord_id = ?;
        """

        self._cursor.execute(query, (discord_id,))
        result: list[str] = self._cursor.fetchall()
        return [item[0] for item in result]

    def transfer_item_to_player(self, pickle_path: str, discord_id: int) -> None:
        # Find the item_id from the items table using the pickle path
        select_query: str = "SELECT id FROM items WHERE object = ?"
        self._cursor.execute(select_query, (pickle_path,))
        item_id: str = self._cursor.fetchone()[0]

        # Update the inventory to assign this item to the new player
        update_query = "UPDATE eq SET player_discord_id = ? WHERE item_id = ?"
        self._cursor.execute(update_query, (discord_id, item_id))
        self._connection.commit()


    
    
