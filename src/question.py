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
        self.conflicts = 0
        self.intersect_questions = {}
        self.filled_blocks = 0

    def __eq__(self, other):
        return self.idx == other.idx

    def add_possible_answers(self, possible_answers: [], answers_by_source: {}):
        self.possible_answers = possible_answers
        self.answers_by_source = answers_by_source


class Intersect:
    def __init__(self, current_question_position: int, intersect_question_position: int, intersect_question: Question):
        self.current_question_position = current_question_position
        self.intersect_question_position = intersect_question_position
        self.intersect_question = intersect_question
