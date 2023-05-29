import random

# Random selection options
COLORS = ["yellow", "white", "green", "red", "orange", "blue", "purple", "black"]
SHAPES = ["rectangle", "circle", "triangle", "square"]
QUESTIONS = [
    "background color",
    "shape",
    "shape text",
    "shape color",
    "number color",
    "text background color",
]


# Create random square options
class Square:
    def __init__(self):
        self.background_color = random.choice(COLORS)
        self.number_color = random.choice(COLORS)
        self.text_background_color = random.choice(COLORS)
        self.shape_color = random.choice(
            [
                color
                for color in COLORS
                if color
                not in [
                    self.background_color,
                    self.text_background_color,
                    self.number_color,
                ]
            ]
        )
        self.shape_text = random.choice(SHAPES)
        self.color_text = random.choice(COLORS)  # color text
        self.shape = random.choice(SHAPES)


# Create the puzzle of 4 random squares, question and good answer
class PuzzleGenerator:
    def __init__(self) -> None:
        self.indexes = [1, 2, 3, 4]
        self.squares = []
        self.question = ""
        self.good_answer = ""

    def generate(self):
        random.shuffle(self.indexes)
        self.squares = [Square() for _ in range(4)]

        # Randomly chosen questions with a label
        q1 = random.choice(QUESTIONS).upper()
        i1 = random.choice(self.indexes)
        q2 = random.choice([i for i in QUESTIONS if i != q1]).upper()
        i2 = random.choice([i for i in self.indexes if i != i1])
        self.question = f"{q1} ({i1}) AND {q2} ({i2})"

        ga1 = getattr(
            self.squares[self.indexes.index(i1)], q1.replace(" ", "_").lower()
        )
        ga2 = getattr(
            self.squares[self.indexes.index(i2)], q2.replace(" ", "_").lower()
        )
        self.good_answer = f"{ga1} {ga2}"
