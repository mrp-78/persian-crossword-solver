from src.crossword import CrossWord
from src.enums import Direction


class Evaluation:
    def __init__(self, crossword: CrossWord):
        self.crossword = crossword
        self.evaluation_table = self.calculate_evaluation_table()

    def calculate_evaluation_table(self):
        table = [[None for j in range(self.crossword.cols)] for i in range(self.crossword.rows)]
        for question in self.crossword.questions:
            ans = self.crossword.get_calculated_answer(question)
            vx = 0
            vy = 0
            if question.direction == Direction.HORIZONTAL:
                vy = 1
            else:
                vx = 1
            for i in range(question.length):
                if ans != '':
                    table[question.x + vx * i][question.y + vy * i] = ans[i] == question.answer[i]
        return table

    def get_accuracy_and_precision(self):
        t, f = 0, 0
        for i in range(self.crossword.rows):
            for j in range(self.crossword.cols):
                if self.evaluation_table[i][j]:
                    t += 1
                elif self.evaluation_table[i][j] is False:
                    f += 1
                else:
                    pass
        accuracy = t / (self.crossword.rows * self.crossword.cols - self.crossword.black_blocks)
        precision = t / (t+f)
        return accuracy, precision

    def get_modules_recall(self):
        modules_recall = {}
        for key in self.crossword.questions[0].possible_answers:
            t = 0
            for question in self.crossword.questions:
                predicted_answer = self.crossword.get_calculated_answer(question)
                if predicted_answer in question.possible_answers[key]:
                    t += 1
            modules_recall[key] = t / len(self.crossword.questions)
        return modules_recall
