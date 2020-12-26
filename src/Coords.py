# -*- coding: utf-8 -*-

class Coordinate:
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.x2 = x1, x2
        self.y1, self.y2 = y1, y2

    def to_string(self):
        return f"{self.x1},{self.y1},{self.x2},{self.y2}"
        
# Emulator window
emulator = Coordinate(0,0,0,0)

# One-row question
question = Coordinate(0,0,0,0)

# Answers, calculated over a one-row question
answers = [
    Coordinate(0,0,0,0),
    Coordinate(0,0,0,0),
    Coordinate(0,0,0,0)
]

# 'Pixel shift' of the answers's buttons, when question is of
# respectively 1, 2, 3 or 4 rows
answers_shift = [0,0,0,0]
