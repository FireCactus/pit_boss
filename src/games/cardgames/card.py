from typing import Optional
permitted_values: list[str] = [
"A",
"2",
"3",
"4",
"5",
"6",
"7",
"8",
"9",
"10",
"J",
"Q",
"K"
]

permitted_colors: list[str] = [
"Hearts",
"Diamonds",
"Spades",
"Clubs"
]

class Card:
    def __init__(self, Value: str, Color: str, face_down: bool=False) -> None:
        
        if Value in permitted_values:
            self.value: str = Value
        else:
            raise ValueError(f"Invalid value: \"{Value}\" for class Card \n Permitted values are: {permitted_values}")

        if Color in permitted_colors:
            self.color: str = Color
        else:
            raise ValueError(f"Invalid color: \"{Color}\" for class Card \n Permitted colors are: {permitted_colors}")

        self.face_down: bool = face_down
    
    def get_value(self) -> Optional[str]:
        if self.face_down:
            return None
        else:
            return self.value

    def get_color(self) -> Optional[str]:
        if self.face_down:
            return None
        else:
            return self.color
    
    def turn_over(self) -> None:
        if self.face_down:
            self.face_down = False
        else:
            self.face_down = True
    
    def get_color_emoji(self) -> Optional[str]:
        if self.face_down:
            return None

        if self.color == "Hearts":
            return "♥️"
        elif self.color == "Diamonds":
            return "♦️"
        elif self.color == "Spades":
            return "♠️"
        elif self.color == "Clubs":
            return "♣️"
        assert False