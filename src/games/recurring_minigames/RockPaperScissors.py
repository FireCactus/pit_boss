from games.recurring_minigames import RecurringMinigame
import random

class RockPaperScissors(RecurringMinigame):
    _options: list[str]
    def __init__(self) -> None:
        self._options = ["Rock", "Paper", "Scissors"]
        self._win_amount = 150
        self._refresh_period_seconds = 60 * 60 * 24 * 3

    def _determine_win(self, player_pick: str) -> str:
        if player_pick not in self._options:
            raise ValueError(f"Player pick is not one of the options, Player picked: {player_pick}, expected {self._options}")

        result: str = random.choice(self._options)
        if result == player_pick:
            return "Draw"
            
        if result == "Rock" and player_pick == "Scissors":
            return "Lose"
        if result == "Rock" and player_pick == "Paper":
            return "Win"
        
        if result == "Paper" and player_pick == "Rock":
            return "Lose"
        if result == "Paper" and player_pick == "Scissors":
            return "Win"
        
        if result == "Scissors" and player_pick == "Paper":
            return "Lose"
        if result == "Scissors" and player_pick == "Rock":
            return "Win"
        assert False

game = RockPaperScissors()
game._determine_win