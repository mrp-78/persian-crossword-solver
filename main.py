from enum import Enum
from copy import deepcopy
from suds.client import Client


class FarsNet:
    def __init__(self):
        self.api_key = 'ed05dc4e-b1f4-46b5-afdc-6a0239122197'
        self.synset_service = Client('http://farsnet.nlp.sbu.ac.ir/WebAPI/services/SynsetService?WSDL')
        self.sense_service = Client('http://farsnet.nlp.sbu.ac.ir/WebAPI/services/SenseService?WSDL')

    def get_synonyms(self, keyword: str):
        synonyms = []
        synsets = self.synset_service.service.getSynsetsByWord(self.api_key, 'EXACT', keyword)
        for synset in synsets:
            senses = self.sense_service.service.getSensesBySynset(self.api_key, synset.id)
            for sense in senses:
                if sense.value not in synonyms:
                    synonyms.append(sense.value)
        return synonyms


class Direction(Enum):
    HORIZONTAL = 1
    VERTICAL = 2


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


class CrossWord:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.questions = []
        self.crossword_table = [[None for j in range(cols)] for i in range(rows)]
        self.farsnet = FarsNet()

    def add_blocked_cell(self, x: int, y: int):
        self.crossword_table[x][y] = '#'

    def read_blocked_cells(self):
        inp = input('مختصات خانه‌های سیاه جدول را در هر سطر وارد کنید و در انتها مقدار end را وارد کنید:\n')
        while inp != 'end':
            x, y = map(int, inp.split())
            self.add_blocked_cell(x-1, y-1)
            inp = input()

    def read_questions(self):
        question_number = 1
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
                print('سوال', str(question_number), ': افقی - خانه', f'({x+1}, {y+1}) -', 'طول:', str(j-y))
                q = input()
                question_number += 1
                question = Question(q, x, y, j-y, direction)
                question.add_possible_answers(self.farsnet.get_synonyms(q))
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
                print('سوال', str(question_number), ': عمودی - خانه', f'({x+1}, {y+1}) -', 'طول:', str(i-y))
                q = input()
                question_number += 1
                question = Question(q, x, y, i - x, direction)
                question.add_possible_answers(self.farsnet.get_synonyms(q))
                self.questions.append(question)
                x = i + 1

    def print_table(self):
        for j in range(self.cols - 1, -1, -1):
            print(f'  {j+1} ', end='')
        print()
        print('-' * (4 * self.cols + 1))
        for i in range(self.rows):
            print(f'{i+1} ', end='')
            for j in range(self.cols):
                value = self.crossword_table[i][j]
                if not value:
                    value = ' '
                if j != self.cols-1:
                    print('| ' + value, end=' ')
                else:
                    print(f'| {value} |')
            print('-' * (4 * self.cols + 1))

    def solve(self):
        returned_table = self.csp(self.crossword_table, 0)
        if returned_table:
            self.crossword_table = returned_table
        self.print_table()

    def csp(self, table, question_number):
        questions = self.questions
        if question_number >= len(questions):
            return table
        current_question = questions[question_number]
        for ans in current_question.possible_answers:
            new_table = self.fill_answer_in_table(deepcopy(table), current_question, ans)
            if new_table:
                returned_table = self.csp(deepcopy(new_table), question_number + 1)
                if returned_table:
                    return returned_table
        return False

    def fill_answer_in_table(self, table: [[]], question: Question, answer: str):
        if len(answer) != question.length:
            return False
        x = question.x
        y = question.y
        if question.direction == Direction.HORIZONTAL:
            for i in range(len(answer)):
                if table[x][y + i] and table[x][y + i] != answer[i]:
                    return False
                table[x][y + i] = answer[i]
        else:
            for i in range(len(answer)):
                if table[x + i][y] and table[x + i][y] != answer[i]:
                    return False
                table[x + i][y] = answer[i]
        return table


def main():
    global crossword
    rows = int(input('تعداد سطرهای جدول:\n'))
    cols = int(input('تعداد ستون‌های جدول:\n'))
    crossword = CrossWord(rows, cols)
    crossword.read_blocked_cells()
    crossword.read_questions()
    crossword.solve()


if __name__ == '__main__':
    crossword: CrossWord
    main()
