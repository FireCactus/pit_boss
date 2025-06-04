import asyncio
from discord import User
import pickle

from player import Item
from database.PlayersDatabase import PlayersDatabase

db = PlayersDatabase()


class Player:
    _min_bet: int = 25
    _max_bet: int = 1000000000000
    _daily_amount: int = 100

    discord_id: int
    display_name:str
    discord_user: User

    def __init__(self, discord_user: User) -> None:
        
        self.discord_user = discord_user

        self.discord_id = discord_user.id
        self.display_name = str(discord_user)
        

        # Add player to db if doesnt exist
        if db.check_if_player_exists(self.discord_id) == False:
            db.add_new_player(self.discord_id, self.display_name)
        
        

    def get_balance(self) -> int:
        balance: int = db.get_player_balance(self.discord_id)
        return balance

    def modify_balance(self, amount: int) -> None:
        db.update_player_balance(self.discord_id, amount)
    
    def change_bet(self, amount: int) -> None:

        if amount < self._min_bet:
            raise ValueError("Bet size too small, minimum bet is {self._min_bet}")
        
        if amount > self._max_bet:
            raise ValueError("Bet size too big, maximum bet is {self._max_bet}")
        
        if self.get_balance() < amount:
            raise ValueError("Bet size is bigger than player balance")

        db.change_player_bet(self.discord_id, amount)

    def get_player_bet(self) -> int:
        result = db.get_player_bet(self.discord_id)
        return result

    def receive_daily(self) -> None:
        if db.check_if_player_received_daily(self.discord_id):
            raise ValueError("Daily already received!")
        else:
            db.change_player_received_daily(self.discord_id, True)
            self.modify_balance(self._daily_amount)

    def save_item_to_inventory(self, item: Item) -> None:
        item.save_to_disk()
        db.save_item_to_player_inventory(self.discord_id, item.get_filepath())

    def delete_item_from_inventory(self, item: Item) -> None:
        db.delete_item_from_player_inventory(item.get_filepath())
        item.delete_from_disk()
    
    def get_all_items(self) -> list[Item]:
        object_pickles: list[str] = db.get_player_items(self.discord_id)
        items: list[Item] = []

        for pickle_path in object_pickles:
            try:
                with open(pickle_path, "rb") as f:
                    item = pickle.load(f)
                    items.append(item)
            except (FileNotFoundError, pickle.UnpicklingError) as e:
                print(f"Error while unpickling object: {pickle_path}:\n{e}")

        return items
    
    def give_item_to_player(self, item:Item, player: "Player") -> None:
        db.transfer_item_to_player(item.get_filepath(), player.discord_id)

        
        