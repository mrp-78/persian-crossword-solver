from src.enums import Direction


class Question:
    def __init__(self, question: str, x: int, y: int, length: int, direction: Direction, answer: str = ''):
        self.question = question
        self.x = x
        self.y = y
        self.length = length
        self.direction = direction
        self.answer = answer
        self.possible_answers = []

    def add_possible_answers(self, possible_answers):
        self.possible_answers += possible_answers
