from lootboxes import LootBox, LootBoxItem
from scratch_off.DiamondRush import DiamondRush
from scratch_off.EmojiLines import EmojiLines
from scratch_off.TransportSearch import TransportSearch
from scratch_off.SuperPayout import SuperPayout

class CommonLootBox(LootBox):
    _price = 100
    _name = "Common loot box"
    _label = "🗝️"
    _winnable_items = [
        LootBoxItem(name="1x Diamond Rush ticket", probability=0.15, amount=1, item_class=DiamondRush),
        LootBoxItem(name="2x Diamond Rush ticket", probability=0.1, amount=2, item_class=DiamondRush),
        
        LootBoxItem(name="1x Emoji Lines ticket", probability=0.15, amount=1, item_class=EmojiLines),
        LootBoxItem(name="2x Emoji Lines ticket", probability=0.1, amount=2, item_class=EmojiLines),
        
        LootBoxItem(name="1x Transport Search ticket", probability=0.15, amount=1, item_class=TransportSearch),
        LootBoxItem(name="2x Transport Search ticket", probability=0.1, amount=2, item_class=TransportSearch),
        
        LootBoxItem(name="1x Super Payout ticket", probability=0.15, amount=1, item_class=SuperPayout),
        LootBoxItem(name="2x Super Payout ticket", probability=0.1, amount=2, item_class=SuperPayout)
        ]
