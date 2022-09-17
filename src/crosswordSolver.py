import logging
from src.crossword import CrossWord
from src.enums import AppEnvironment
from src.question import Question
from src.evaluation import Evaluation
from copy import deepcopy
from heapq import heappop, heappush, heapify
from decouple import config
from src.answers import Answers
from src.normalizer import Normalizer
from src.crosswordUtils import fill_answer_in_table


class CrosswordSolver:
    def __init__(self, crossword: CrossWord, print_answers):
        self.crossword = crossword
        self.answer_collector = Answers(print_answers)
        self.normalizer = Normalizer()
        self.best_answer = None

    def solve(self):
        for question in self.crossword.questions:
            res = self.answer_collector.collect_answers(question)
            if res:
                self.crossword.questions_with_answer += 1
        self.crossword.questions.sort(key=lambda x: len(x.possible_answers))
        self.csp()
        self.crossword = self.best_answer
        if config('APP_ENV') == AppEnvironment.DEVELOPMENT.value:
            evaluation = Evaluation(self.crossword)
            evaluation.print_results()
            self.crossword.evaluation_table = evaluation.evaluation_table
        return self.crossword

    def csp(self):
        i = 0
        heap = []
        heapify(heap)
        crossword_table = deepcopy(self.crossword)
        crossword_table.score = 0.001
        heappush(heap, crossword_table)
        while len(heap) > 0:
            i += 1
            if i % 50000 == 0:
                logging.info(f'state number={i} heap length={len(heap)}')
            crossword_table: CrossWord = heappop(heap)
            question_number = crossword_table.current_question
            if crossword_table.filled_questions >= len(self.crossword.questions):
                self.best_answer = crossword_table
                return
            if crossword_table.current_question >= len(self.crossword.questions):
                continue
            if self.best_answer is not None and len(
                    self.crossword.questions) - question_number + crossword_table.filled_questions < self.best_answer.filled_questions:
                if question_number <= len(self.crossword.questions) - 5:
                    logging.warning(
                        f'prune question_number={question_number} filled_questions={crossword_table.filled_questions} best_answer.filled_questions={self.best_answer.filled_questions} len(heap)={len(heap)}')
                continue
            ct: CrossWord = deepcopy(crossword_table)
            ct.current_question += 1
            heappush(heap, ct)
            current_question: Question = self.crossword.questions[question_number]
            answers = dict(sorted(current_question.possible_answers.items(), key=lambda item: item[1], reverse=True))
            for ans in answers:
                new_table, cb = fill_answer_in_table(deepcopy(crossword_table), ans)
                if new_table:
                    ct: CrossWord = new_table
                    ct.score = (crossword_table.filled_questions + 1) / len(self.crossword.questions) + \
                               (crossword_table.filled_questions + cb) / (self.crossword.rows * self.crossword.cols)
                    ct.current_question += 1
                    ct.filled_questions += 1
                    ct.conflicted_blocks += cb
                    ct.questions_with_answer -= 1
                    heappush(heap, ct)
                    if self.best_answer is None \
                            or ct.score > self.best_answer.score \
                            or ct.filled_questions > self.best_answer.filled_questions:
                        self.best_answer = ct
        logging.info(f'{self.crossword.file_name}: searches_states={i}')
