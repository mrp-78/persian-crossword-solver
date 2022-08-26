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
        self.possible_answers = []
        self.answers_by_source = {}

    def add_possible_answers(self, possible_answers: [], answers_by_source: {}):
        self.possible_answers = possible_answers
        self.answers_by_source = answers_by_source
