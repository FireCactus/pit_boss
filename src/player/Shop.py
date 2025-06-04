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

class UnlimitedShopItem(NamedTuple):
    item_type: Type[Item]

class LimitedShopItem(NamedTuple):
    item_type: Type[Item]
    restock_probability: float # from 0 to 1, the probability of the item appearing in stock 
    restock_min: int # minumu amount of this item in the restock
    restock_max: int # maximum amount of this item in the restock
    
    

class Shop:

    def __init__(self) -> None:
        self.possible_shop_items: list[ShopItem] = [
            UnlimitedShopItem(SuperPayout),
            UnlimitedShopItem(EmojiLines),
            UnlimitedShopItem(XMarksTheSpot),
            UnlimitedShopItem(TransportSearch),
            UnlimitedShopItem(DiamondRush)
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

    def restock_unlimited_shop_items(self, delete_old_items: bool = True) -> None:
        
        if delete_old_items:
            for item in self.get_items_in_stock():
                for shop_item in self.possible_shop_items:
                    if isinstance(item, shop_item.item_type) and isinstance(shop_item, UnlimitedShopItem):
                        self.delete_item_from_stock(item)
                        break

        for possible_item in self.possible_shop_items:
            if not isinstance(possible_item, UnlimitedShopItem):
                continue

            item = possible_item.item_type()
            item.save_to_disk()
            db.save_item_to_player_inventory(db._shop_discord_id, item.get_filepath())
    
    def restock_limited_shop_items(self) -> None:
        

        for item in self.get_items_in_stock():
            for item in self.get_items_in_stock():
                for shop_item in self.possible_shop_items:
                    if isinstance(item, shop_item.item_type) and isinstance(shop_item, LimitedShopItem):
                        self.delete_item_from_stock(item)

        for possible_item in self.possible_shop_items:
            
            if not isinstance(possible_item, LimitedShopItem):
                continue

            if possible_item.restock_probability < random.random():
                continue

            item_amount: int = random.randint(possible_item.restock_min, possible_item.restock_max)

            for _ in range(item_amount):
                
                item = possible_item.item_type()
                item.save_to_disk()
                db.save_item_to_player_inventory(db._shop_discord_id, item.get_filepath())
    