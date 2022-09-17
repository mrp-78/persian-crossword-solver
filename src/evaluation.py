from src.enums import Direction
from src.crosswordUtils import get_calculated_answer


class Evaluation:
    def __init__(self, crossword):
        self.crossword = crossword
        self.evaluation_table = self.calculate_evaluation_table()

    def calculate_evaluation_table(self):
        table = [[None for j in range(self.crossword.cols)] for i in range(self.crossword.rows)]
        for question in self.crossword.questions:
            ans = get_calculated_answer(self.crossword, question)
            vx = 0
            vy = 0
            if question.direction == Direction.HORIZONTAL:
                vy = 1
            else:
                vx = 1
            for i in range(question.length):
                if ans != '':
                    if ans[i] != ' ':
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
        for key in self.crossword.questions[0].answers_by_source:
            t = 0
            for question in self.crossword.questions:
                predicted_answer = get_calculated_answer(self.crossword, question)
                if predicted_answer in question.answers_by_source[key]:
                    t += 1
            modules_recall[key] = t / len(self.crossword.questions)
        return modules_recall

    def print_results(self):
        accuracy, precision = self.get_accuracy_and_precision()
        modules_recall = self.get_modules_recall()
        print(f'accuracy = {accuracy}\nprecision = {precision}')
        for key in modules_recall:
            print(f'module {key}: recall = {modules_recall[key]}')
