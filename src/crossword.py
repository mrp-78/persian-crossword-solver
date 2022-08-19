import re
from src.farsnet import FarsNet
from src.farsiyar import FarsiYar
from src.enums import Direction
from src.question import Question
from copy import deepcopy
from colorama import Fore, Back, Style
from src.normalizer import Normalizer


class CrossWord:
    def __init__(self, file_name: str, print_answers=True, read_answers=False):
        self.farsnet = FarsNet()
        self.farsiyar = FarsiYar()
        self.file_name = file_name
        self.questions = []
        self.crossword_table = [[]]
        self.rows = 0
        self.cols = 0
        self.black_blocks = 0
        self.read_answers = read_answers
        self.print_answers = print_answers
        self.read_data_from_file()
        self.normalizer = Normalizer()

    def read_data_from_file(self):
        with open(f'{self.file_name}', encoding='utf-8') as f:
            self.rows, self.cols = map(int, f.readline().split())
            self.crossword_table = [[None for j in range(self.cols)] for i in range(self.rows)]
            blocks = f.readline()
            for i in range(len(blocks)):
                if blocks[i] == '1':
                    self.black_blocks += 1
                    self.crossword_table[i // self.cols][i % self.cols] = '#'
            questions_list = re.split('(&|#|@)', f.readline())
            answers_list = False
            if self.read_answers:
                answers_list = re.split('(&|#|@)', f.readline())
            self.read_questions(questions_list, answers_list)

    def remove_special_chars_from_list(self, questions_list: []):
        for q in questions_list:
            if re.match('[&#@\-\n]', q) or q == '':
                continue
            yield q

    def read_questions(self, questions_list: [], answers_list):
        all_questions = self.remove_special_chars_from_list(questions_list)
        if answers_list:
            all_answers = self.remove_special_chars_from_list(answers_list)
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
                ans = ''
                if answers_list:
                    ans = next(all_answers)
                question = Question(question_number, next(all_questions), x, y, j - y, direction, ans)
                question_number += 1
                self.questions.append(question)
                y = j + 1
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
                ans = ''
                if answers_list:
                    ans = next(all_answers)
                question = Question(question_number, next(all_questions), x, y, i - x, direction, ans)
                question_number += 1
                self.questions.append(question)
                x = i + 1

    def print_table(self, is_empty: bool = False):
        for j in range(self.cols - 1, -1, -1):
            print(f'  {j + 1} ', end='')
        print()
        if not is_empty:
            print(' ', end='')
        print(Style.BRIGHT + Back.BLACK + Fore.LIGHTWHITE_EX + "-" * (4 * self.cols + 1))
        start_col, end_col, step = 0, self.cols, 1
        if is_empty:
            start_col, end_col, step = self.cols - 1, -1, -1
        for i in range(self.rows):
            if not is_empty:
                print(f' {i + 1} ', end='')
            for j in range(start_col, end_col, step):
                value = self.crossword_table[i][j]
                if not value:
                    value = ' '
                if value == '#':
                    print(Style.BRIGHT + Back.BLACK + Fore.LIGHTWHITE_EX + '|', end='')
                    print(Style.BRIGHT + Back.LIGHTWHITE_EX + Fore.LIGHTWHITE_EX + f' {value} ', end='')
                else:
                    print(Style.BRIGHT + Back.BLACK + Fore.LIGHTWHITE_EX + f'| {value} ', end='')
            print(Style.BRIGHT + Back.BLACK + Fore.LIGHTWHITE_EX + '|', end='')
            if is_empty:
                print(f' {i + 1} ', end='')
            print()
            if not is_empty:
                print(' ', end='')
            print(Style.BRIGHT + Back.BLACK + Fore.LIGHTWHITE_EX + '-' * (4 * self.cols + 1))

    def solve(self):
        self.get_possible_answers()
        returned_table = self.csp(self.crossword_table, 0)
        if returned_table:
            self.crossword_table = returned_table

    def get_possible_answers(self):
        for question in self.questions:
            possible_answers = self.farsnet.get_synonyms(question.question)
            question.add_possible_answers(possible_answers, 'FarseNet')
            possible_answers = self.farsiyar.get_synonyms(question.question)
            question.add_possible_answers(possible_answers, 'FarsiYar')
            if self.print_answers:
                print(f'question #{question.idx} - {question.direction} - ({question.x}, {question.y}) - length: {question.length} :')
                print(f'\tquestion: {question.question}')
                print(f'\tpossible answers: {question.possible_answers}\n')

    def csp(self, table, question_number):
        questions = self.questions
        if question_number >= len(questions):
            return table
        current_question = questions[question_number]
        possible_answers = set()
        for key in current_question.possible_answers:
            possible_answers.update(current_question.possible_answers[key])
        for ans in possible_answers:
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

    def get_calculated_answer(self, question: Question):
        if question.predicted_answer:
            return question.predicted_answer
        ans = ''
        vx = 0
        vy = 0
        if question.direction == Direction.HORIZONTAL:
            vy = 1
        else:
            vx = 1
        for x in range(question.length):
            ch = self.crossword_table[question.x + vx*x][question.y + vy*x]
            if ch is not None:
                ans += ch
        value = self.normalizer.normalize(ans)
        question.predicted_answer = value
        return value
