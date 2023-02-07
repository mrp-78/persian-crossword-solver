import logging
import time
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
        self.coefficients = [1, 4, 2]

    def solve(self):
        for question_id in self.crossword.questions:
            res = self.answer_collector.collect_answers(self.crossword.questions[question_id])
            if res:
                self.crossword.forward_questions.append(self.crossword.questions[question_id])
        self.csp()
        self.crossword = self.best_answer
        if config('APP_ENV') == AppEnvironment.DEVELOPMENT.value:
            evaluation = Evaluation(self.crossword)
            evaluation.print_results()
            self.crossword.evaluation_table = evaluation.evaluation_table
        return self.crossword

    def csp(self):
        start_time = time.time()
        i = 0
        heap = []
        heapify(heap)
        crossword_table = deepcopy(self.crossword)
        crossword_table.score = 0.001
        crossword_table.forward_questions.sort(key=lambda x: len(x.intersect_questions))
        heappush(heap, crossword_table)
        while len(heap) > 0:
            if time.time() - start_time >= 2 * 60:
                logging.info('timeout')
                return
            i += 1
            if i % 10000 == 0:
                logging.info(f'state number={i} heap length={len(heap)}')
            crossword_table: CrossWord = heappop(heap)
            if self.best_answer is not None and \
                    crossword_table.heuristic < self.best_answer.score:
                if len(crossword_table.forward_questions) > 7:
                    logging.warning(
                        f'prune remaining_questions={len(crossword_table.forward_questions)} filled_questions={crossword_table.filled_questions} best_answer.filled_questions={self.best_answer.filled_questions} len(heap)={len(heap)}')
                continue

            # Dynamic Variable Ordering
            # crossword_table.forward_questions.sort(key=lambda x: len(x.possible_answers), reverse=True) # because of using pop functon we need to use reverse
            # crossword_table.forward_questions.sort(key=lambda x: len(x.intersect_questions))
            try:
                current_question: Question = crossword_table.forward_questions.pop()
                crossword_table.past_questions.append(current_question)
            except Exception as e:
                continue
            heappush(heap, deepcopy(crossword_table))

            answers = dict(sorted(current_question.possible_answers.items(), key=lambda item: item[1], reverse=True))
            # answers = current_question.possible_answers
            for ans in answers:
                new_table, cb = fill_answer_in_table(deepcopy(crossword_table), current_question, ans)
                if new_table:
                    ct: CrossWord = new_table
                    ct.filled_questions += 1
                    ct.conflicted_blocks += cb
                    ct.sop += answers[ans]
                    ct.score = self.calculate_score(ct.filled_questions, ct.conflicted_blocks, ct.sop)
                    if ct.filled_questions == len(self.crossword.questions):
                        self.best_answer = ct
                        return
                    answer_verified, heuristic = self.forward_checking(ct, current_question, ans, cb > 0)
                    ct.heuristic = heuristic
                    # Arc-consistency
                    if not answer_verified:
                        continue
                    if self.best_answer is not None and heuristic < self.best_answer.score:
                        if len(ct.forward_questions) > 7:
                            logging.warning(
                                f'prune remaining_questions={len(ct.forward_questions)} filled_questions={ct.filled_questions} best_answer.filled_questions={self.best_answer.filled_questions} len(heap)={len(heap)}')
                        continue
                    if self.best_answer is None \
                            or ct.score > self.best_answer.score:
                        self.best_answer = ct
                    heappush(heap, ct)
        logging.info(f'{self.crossword.file_name}: searches_states={i}')

    def forward_checking(self, crossword: CrossWord, question: Question, answer: str, answer_verified: bool):
        verified = answer_verified
        fq, cb, sop = crossword.filled_questions, crossword.conflicted_blocks, crossword.sop
        for q in list(crossword.forward_questions):
            qid = q.idx
            if qid in question.intersect_questions:
                p1, p2 = question.intersect_questions[qid]
                new_possible_answers = dict(
                    filter(lambda ans: ans[0][p2] == answer[p1], crossword.questions[qid].possible_answers.items())
                )
                crossword.questions[qid].possible_answers = new_possible_answers
                if len(new_possible_answers) > 0:
                    verified = True
                    fq += 1
                    sop += new_possible_answers[max(new_possible_answers, key=new_possible_answers.get)]
                    conflicts = len(q.intersect_questions) - q.filled_blocks
                    if conflicts < 0:
                        raise Exception(f'Invalid value for conflicts for question {q.idx}')
                    cb += conflicts
                else:
                    crossword.forward_questions.remove(q)
            else:
                fq += 1
                sop += q.possible_answers[max(q.possible_answers, key=q.possible_answers.get)]
                conflicts = len(q.intersect_questions) - q.filled_blocks
                if conflicts < 0:
                    raise Exception(f'Invalid value for conflicts for question {q.idx}')
                cb += conflicts
        heuristic = self.calculate_score(fq, cb, sop)
        return verified, heuristic

    def calculate_score(self, filled_questions: int, conflicted_blocks: int, sop: int):
        return (self.coefficients[0] * filled_questions / len(self.crossword.questions) +
                self.coefficients[1] * conflicted_blocks / (self.crossword.rows * self.crossword.cols - self.crossword.black_blocks) +
                self.coefficients[2] * sop / filled_questions) / sum(self.coefficients)
