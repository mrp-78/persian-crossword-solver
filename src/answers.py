from src.question import Question
from src.farsnet import FarsNet
from src.farsiyar import FarsiYar
from src.normalizer import Normalizer


class Answers:
    def __init__(self, print_answers):
        self.print_answers = print_answers
        self.farsnet = FarsNet()
        # self.farsiyar = FarsiYar()
        self.normalizer = Normalizer()

    def collect_answers(self, question: Question):
        answers_by_source = set()
        answers_probability = {}
        question_text = self.normalizer.normalize(question.question)
        answers_by_source = self.get_synonyms(question_text, question.length)
        for key in answers_by_source:
            for ans in answers_by_source[key]:
                if ans not in answers_probability:
                    answers_probability[ans] = self.get_probability(answers_by_source, ans)
        if self.print_answers:
            print(
                f'question #{question.idx} - {question.direction} - ({question.x}, {question.y}) - length: {question.length} :')
            print(f'\tquestion: {question_text}')
            print(f'\tpossible answers: {answers_by_source}\n')
        question.add_possible_answers(answers_probability, answers_by_source)

    def get_synonyms(self, question, length):
        farsnet_answers, farsiyar_answers = set(), set()
        farsnet_answers.update(self.farsnet.get_synonyms(question))
        # farsiyar_answers.update(self.farsiyar.get_synonyms(question))
        question_words = question.split(' و ')
        if len(question_words) >= 2:
            for word in question_words:
                farsnet_answers.update(self.farsnet.get_synonyms(word))
                # farsiyar_answers.update(self.farsiyar.get_synonyms(word))
        new_farsnet_answers, new_farsiyar_answers = set(), set()
        for ans in farsnet_answers:
            if len(ans) == length:
                new_farsnet_answers.add(ans)
        for ans in farsiyar_answers:
            if len(ans) == length:
                new_farsiyar_answers.add(ans)
        return {'FarsNet': new_farsnet_answers, 'FarsiYar': new_farsiyar_answers}

    def get_probability(self, answers_by_source, answer):
        count = 0
        for key in answers_by_source:
            if answer in answers_by_source[key]:
                count += 1
        return count / (len(answers_by_source)+1)
