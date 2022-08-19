from src.enums import Direction


class Question:
    def __init__(self, idx: int, question: str, x: int, y: int, length: int, direction: Direction, answer: str = ''):
        self.idx = idx
        self.question = question
        self.x = x
        self.y = y
        self.length = length
        self.direction = direction
        self.answer = answer
        self.predicted_answer = None
        self.possible_answers = {}

    def add_possible_answers(self, possible_answers: [], source: str):
        answers = [word for word in possible_answers if len(word) == self.length]
        self.possible_answers[source] = answers
