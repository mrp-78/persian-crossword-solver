from copy import deepcopy


class CrossWordTable:
    def __init__(self, table: [[]], score: float, current_question: int, filled_questions: int, filled_blocks: int):
        self.table = deepcopy(table)
        self.score = score
        self.current_question = current_question
        self.filled_questions = filled_questions
        self.filled_blocks = filled_blocks

    def __lt__(self, other):
        return self.score > other.score

    def __hash__(self):
        return hash(str(self.current_question) + str(self.table))
