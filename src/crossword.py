import re
import logging
from src.enums import Direction, AppEnvironment
from src.question import Question
from src.normalizer import Normalizer
from src.answers import Answers
from src.crosswordTable import CrossWordTable
from src.evaluation import Evaluation
from copy import deepcopy
from colorama import Fore, Back, Style
from heapq import heappop, heappush, heapify
from decouple import config


class CrossWord:
    def __init__(self, file_name: str, print_answers=True, read_answers=True):
        self.answer_collector = Answers(print_answers)
        self.normalizer = Normalizer()
        self.file_name = file_name
        self.questions = []
        self.crossword_table = [[]]
        self.rows = 0
        self.cols = 0
        self.black_blocks = 0
        self.read_answers = read_answers
        self.print_answers = print_answers
        self.read_data_from_file()
        self.best_answer = None
        self.evaluation_table = None

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

    @staticmethod
    def remove_special_chars_from_list(questions_list: []):
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
                question.conflicts = self.calculate_num_of_conflicts(question)
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
                question.conflicts = self.calculate_num_of_conflicts(question)
                question_number += 1
                self.questions.append(question)
                x = i + 1

    def calculate_num_of_conflicts(self, question: Question):
        conflicts = 0
        if question.direction == Direction.HORIZONTAL:
            for j in range(question.length):
                x = question.x
                y = question.y + j
                if x-1 >= 0 and self.crossword_table[x-1][y] != '#':
                    conflicts += 1
                elif x+1 < self.rows and self.crossword_table[x+1][y] != '#':
                    conflicts += 1
        elif question.direction == Direction.VERTICAL:
            for i in range(question.length):
                x = question.x + i
                y = question.y
                if y-1 >= 0 and self.crossword_table[x][y-1] != '#':
                    conflicts += 1
                elif y+1 < self.cols and self.crossword_table[x][y+1] != '#':
                    conflicts += 1
        return conflicts

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
                    if self.evaluation_table is not None and self.evaluation_table[i][j] is not None:
                        print(Style.BRIGHT + Back.BLACK + Fore.LIGHTWHITE_EX + '|', end='')
                        if self.evaluation_table[i][j]:
                            print(Style.BRIGHT + Back.GREEN + Fore.LIGHTWHITE_EX + f' {value} ', end='')
                        else:
                            print(Style.BRIGHT + Back.RED + Fore.LIGHTWHITE_EX + f' {value} ', end='')
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
        for question in self.questions:
            self.answer_collector.collect_answers(question)
        self.questions.sort(key=lambda x: x.conflicts, reverse=True)
        self.csp()
        self.crossword_table = self.best_answer.table
        if config('APP_ENV') == AppEnvironment.DEVELOPMENT.value:
            evaluation = Evaluation(self)
            evaluation.print_results()
            self.evaluation_table = evaluation.calculate_evaluation_table()

    def csp(self):
        i = 0
        heap = []
        heapify(heap)
        crossword_table = CrossWordTable(self.crossword_table, 0.001, 0, 0, 0)
        heappush(heap, crossword_table)
        while len(heap) > 0:
            i += 1
            if i % 50000 == 0:
                logging.info(f'state number={i} heap length={len(heap)}')
            crossword_table: CrossWordTable = heappop(heap)
            question_number = crossword_table.current_question
            if crossword_table.filled_questions >= len(self.questions):
                self.best_answer = crossword_table
                return
            if self.best_answer is not None and len(self.questions) - question_number + crossword_table.filled_questions < self.best_answer.filled_questions:
                if question_number <= len(self.questions) - 5:
                    logging.warning(f'prune question_number={question_number} filled_questions={crossword_table.filled_questions} best_answer.filled_questions={self.best_answer.filled_questions} len(heap)={len(heap)}')
                continue
            if crossword_table.current_question >= len(self.questions):
                continue
            ct = CrossWordTable(
                crossword_table.table,
                crossword_table.score,
                question_number + 1,
                crossword_table.filled_questions,
                crossword_table.filled_blocks
            )
            heappush(heap, ct)
            current_question: Question = self.questions[question_number]
            answers = dict(sorted(current_question.possible_answers.items(), key=lambda item: item[1], reverse=True))
            for ans in answers:
                new_table, cb = self.fill_answer_in_table(deepcopy(crossword_table.table), current_question, ans)
                if new_table:
                    ct = CrossWordTable(
                        new_table,
                        (crossword_table.filled_questions+1) / len(self.questions) + (crossword_table.filled_questions+cb) / (self.rows*self.cols),
                        question_number + 1,
                        crossword_table.filled_questions + 1,
                        crossword_table.filled_questions + cb
                    )
                    heappush(heap, ct)
                    if self.best_answer is None \
                            or ct.score > self.best_answer.score \
                            or ct.filled_questions > self.best_answer.filled_questions:
                        self.best_answer = ct
        logging.info(f'{self.file_name}: searches_states={i}')

    def fill_answer_in_table(self, table: [[]], question: Question, answer: str):
        if len(answer) != question.length:
            return False, 0
        cb = 0
        x = question.x
        y = question.y
        if question.direction == Direction.HORIZONTAL:
            for i in range(len(answer)):
                if table[x][y + i]:
                    if table[x][y + i] != answer[i]:
                        return False, 0
                    else:
                        cb += 1
                        continue
                table[x][y + i] = answer[i]
        else:
            for i in range(len(answer)):
                if table[x + i][y]:
                    if table[x + i][y] != answer[i]:
                        return False, 0
                    else:
                        cb += 1
                        continue
                table[x + i][y] = answer[i]
        return table, cb

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
            else:
                ans += ' '
        question.predicted_answer = ans
        return ans
