from enum import Enum
from copy import deepcopy


class Direction(Enum):
    HORIZONTAL = 1
    VERTICAL = 2


class CrossWord:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.questions = []
        self.crossword_table = [[None for j in range(cols)] for i in range(rows)]

    def add_blocked_cell(self, x: int, y: int):
        self.crossword_table[x][y] = '#'

    def read_blocked_cells(self):
        inp = input('enter black blocks with pairs of (x, y) or type "E" for end: \n')
        while inp != 'E':
            x, y = map(int, inp.split())
            self.add_blocked_cell(x, y)
            inp = input()

    def read_questions(self):
        direction = Direction.HORIZONTAL
        for i in range(self.rows):
            x = i
            y = 0
            for j in range(self.cols):
                while j < self.cols and self.crossword_table[i][j] != '#':
                    j += 1
                if j - y < 2:
                    y = j + 1
                    continue
                print(f'HORIZONTAL ({x}, {y}) length={j-y}')
                q = input('question: ')
                question = Question(q, x, y, j-y, direction)
                ans = input('possible answers separated by comma: ').split(',')
                question.add_possible_answers(ans)
                self.questions.append(question)
                y = j+1
        direction = Direction.VERTICAL
        for j in range(self.cols):
            x = 0
            y = j
            for i in range(self.rows):
                while i < self.rows and self.crossword_table[i][j] != '#':
                    i += 1
                if i - x < 2:
                    x = i + 1
                    continue
                print(f'VERTICAL ({x}, {y}) length={i - x}')
                q = input('question: ')
                question = Question(q, x, y, i - x, direction)
                ans = input('possible answers separated by comma: ').split(',')
                question.add_possible_answers(ans)
                self.questions.append(question)
                x = i + 1

    def print_table(self):
        print('-' * (4 * self.cols + 1))
        for i in range(self.rows):
            for j in range(self.cols):
                value = self.crossword_table[i][j]
                if not value:
                    value = ' '
                if j != self.cols - 1:
                    print('| ' + value, end=' ')
                else:
                    print('| ' + value + ' |')
            print('-' * (4 * self.cols + 1))


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


def csp(table, question_number):
    global crossword
    questions = crossword.questions
    if question_number >= len(questions):
        return table
    current_question = questions[question_number]
    for ans in current_question.possible_answers:
        new_table = fill_answer_in_table(deepcopy(table), current_question, ans)
        if new_table:
            returned_table = csp(deepcopy(new_table), question_number+1)
            if returned_table:
                return returned_table
    return False


def fill_answer_in_table(table: [[]], question: Question, answer: str):
    if len(answer) != question.length:
        return False
    x = question.x
    y = question.y
    if question.direction == Direction.HORIZONTAL:
        for i in range(len(answer)):
            if table[x][y+i] and table[x][y+i] != answer[i]:
                return False
            table[x][y + i] = answer[i]
    else:
        for i in range(len(answer)):
            if table[x+i][y] and table[x+i][y] != answer[i]:
                return False
            table[x+i][y] = answer[i]
    return table


def main():
    global crossword
    rows, cols = map(int, input('please enter number of rows and columns of crossword: ').split())
    crossword = CrossWord(rows, cols)
    crossword.read_blocked_cells()
    crossword.print_table()
    crossword.read_questions()
    crossword.print_table()
    print(csp(crossword.crossword_table, 0))


if __name__ == '__main__':
    crossword: CrossWord
    main()
