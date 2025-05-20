from games import game_player as gp


def renew_all_dailies():
    players = gp.load_all_players()

    for player in players:
        player.received_daily=False
        gp.save_player_to_file(player)


if __name__ == "__main__":
    renew_all_dailies()