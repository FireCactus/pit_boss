import yaml

PLAYER_FILE_NAME="datahub/players.yaml"


class GamePlayer:
    def __init__(self, name, money=0, hands=[], received_daily=False):
        self.name = name
        self.money = money
        self.received_daily = received_daily
        
        self.hands = hands # list of dicts containing cards [{bet:x,cards:[]}, {bet:x,cards:[]}]
        self.roulette_pick_color = None  # string value - red, black, green
        self.roulette_pick_number = None  # string value - odd, even
        self.dealer_cards = []


def load_all_players():
    game_players = []
    with open(PLAYER_FILE_NAME, "r") as stream:
        players = yaml.load_all(stream, yaml.FullLoader)

        for player in players:
            game_player = GamePlayer(player["name"], player['money'], received_daily=player['received_daily'])
            game_players.append(game_player)
    return game_players

def load_player_from_file(player_name):

    with open(PLAYER_FILE_NAME, "r") as stream:
        players = yaml.load_all(stream, yaml.FullLoader)

        for player in players:
            if player["name"] == player_name:
                game_player = GamePlayer(player_name, player['money'], received_daily=player['received_daily'])
                return game_player
        raise ValueError(f"Player {player_name} doesnt exist in player file")


def save_player_to_file(game_player):
    
    with open(PLAYER_FILE_NAME, "r") as stream:
        players = list(yaml.load_all(stream, yaml.FullLoader))

        # Check if the player exists, and update or append
        updated = False
        for player in players:
            if player["name"] == game_player.name:
                player["money"] = game_player.money
                player['received_daily'] = game_player.received_daily
                updated = True
                break

        if not updated:
            players.append({"name": game_player.name, "money": game_player.money, 'received_daily':game_player.received_daily})

    # Write back all players to the file
    with open(PLAYER_FILE_NAME, "w") as stream:

        yaml.dump_all(players, stream)

