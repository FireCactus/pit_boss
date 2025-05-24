from database.PlayersDatabase import PlayersDatabase

db = PlayersDatabase()

class Player:
    _min_bet: int = 25
    _max_bet: int = 1000000000000
    _daily_amount: int = 75
    
    def __init__(self, name: str) -> None:
        self.name: str = name

        # Add player to db if doesnt exist
        if db.check_if_player_exists(self.name) == False:
            db.add_new_player(self.name)

    def get_balance(self) -> int:
        balance: int = db.get_player_balance()
        return balance

    def modify_balance(self, amount: int) -> None:
        db.update_player_balance(self.name, amount)
    
    def change_bet(self, amount: int) -> None:

        if amount < self._min_bet:
            raise ValueError("Bet size too small, minimum bet is {self._min_bet}")
        
        if amount > self._max_bet:
            raise ValueError("Bet size too big, maximum bet is {self._max_bet}")
        
        if self.get_balance() < amount:
            raise ValueError("Bet size is bigger than player balance")

        db.change_player_bet(self.name, amount)
    

    def receive_daily(self) -> None:
        if db.check_if_player_received_daily(self.name):
            raise ValueError("Daily already received!")
        else:
            db.change_player_received_daily(self.name, True)
            self.modify_balance(self._daily_amount)
        