import game_player as player

class RouletteGame:
    def __init__(self, min_bet=25, max_bet=1000):
        self.players = []

        self.min_bet = min_bet
        self.max_bet = max_bet
        self.max_players = max_players

    def add_player_to_game(self, player):

        if type(player) is player.GamePlayer:
            raise ValueError(f"player is not GamePlayer but {type(player)}")
            
        
        elif player.money < self.min_bet:
            raise ValueError(f"Player doesnt have enough money to play! \n minimal bet is {self.min_bet}, player has {player.money}")
        
        elif player not in self.players:
            self.players.append(player)

            
    def remove_player(self, player):
        if player not in self.players:
            return

        self.players.remove(player)