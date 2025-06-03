from discord import User
import pickle
import random
from typing import *

from player import Item
from database.PlayersDatabase import PlayersDatabase

from games.scratch_off.TransportSearch import TransportSearch
from games.scratch_off.DiamondRush import DiamondRush
from games.scratch_off.EmojiLines import EmojiLines
from games.scratch_off.SuperPayout import SuperPayout
from games.scratch_off.XMarksTheSpot import XMarksTheSpot


db = PlayersDatabase()

class ShopItem(NamedTuple):
    item_type: Type[Item]
    restock_probability: float # from 0 to 1, the probability of the item appearing in stock 
    restock_min: int # minumu amount of this item in the restock
    restock_max: int # maximum amount of this item in the restock
    

class Shop:

    def __init__(self) -> None:
        self.possible_shop_items: list[ShopItem] = [
            ShopItem(SuperPayout,     0.8, 2, 6),
            ShopItem(EmojiLines,      0.6, 1, 5),
            ShopItem(XMarksTheSpot,   0.9, 3, 8),
            ShopItem(TransportSearch, 0.5, 1, 4),
            ShopItem(DiamondRush,     0.4, 2, 4),
        ]

    def get_items_in_stock(self) -> list[Item]:
        object_pickles: list[str] = db.get_player_items(db._shop_discord_id)
        items: list[Item] = []

        for pickle_path in object_pickles:
            try:
                with open(pickle_path, "rb") as f:
                    item = pickle.load(f)
                    items.append(item)
            except (FileNotFoundError, pickle.UnpicklingError) as e:
                print(f"Error while unpickling object: {pickle_path}:\n{e}")

        return items
    
    def delete_item_from_stock(self, item: Item) -> None:
        db.delete_item_from_player_inventory(item.get_filepath())
        item.delete_from_disk()
    
    def restock(self) -> None:

        for item in self.get_items_in_stock():
            self.delete_item_from_stock(item)

        for possible_item in self.possible_shop_items:
            rand: float = random.random()
            if possible_item.restock_probability < rand:
                continue

            item_amount: int = random.randint(possible_item.restock_min, possible_item.restock_max)

            for _ in range(item_amount):
                item = possible_item.item_type()
                item.save_to_disk()
                db.save_item_to_player_inventory(db._shop_discord_id, item.get_filepath())
    