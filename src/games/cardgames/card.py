permitted_values = [
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

permitted_colors = [
"Hearts",
"Diamonds",
"Spades",
"Clubs"
]

class Card:
    def __init__(self, Value, Color, face_down=False):
        
        if Value in permitted_values:
            self.value = Value
        else:
            raise ValueError(f"Invalid value: \"{Value}\" for class Card \n Permitted values are: {permitted_values}")

        if Color in permitted_colors:
            self.color = Color
        else:
            raise ValueError(f"Invalid color: \"{Color}\" for class Card \n Permitted colors are: {permitted_colors}")

        self.face_down = face_down
    
    def get_value(self):
        if self.face_down:
            return None
        else:
            return self.value

    def get_color(self):
        if self.face_down:
            return None
        else:
            return self.color
    
    def get_value_and_color(self):
        if self.face_down:
            return None, None
        else:
            return self.value, self.color
    
    def turn_over(self):
        if self.face_down:
            self.face_down = False
        else:
            self.face_down = True
    
    def get_color_emoji(self):
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