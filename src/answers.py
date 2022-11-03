from src.question import Question
from src.modules.farsnet import FarsNet
from src.modules.farsiyar import FarsiYar
from src.modules.es_wikipedia import WikipediaCorpus
from src.normalizer import Normalizer
from src.utils import merge_answers


class Answers:
    def __init__(self, print_answers):
        self.print_answers = print_answers
        self.farsnet = FarsNet()
        self.farsiyar = FarsiYar()
        self.wikipedia_corpus = WikipediaCorpus()
        self.normalizer = Normalizer()

    def collect_answers(self, question: Question):
        answers_probability = {}
        answers_by_source = {
            'FarsNet': {},
            'FarsiYar': {},
            'es_wikipedia': {}
        }
        question_text = self.normalizer.normalize(question.question)
        question_words = question_text.split(' و ')
        answers_by_source = self.get_synonyms(question_text, question.length)
        if len(question_text.split()) == 1:
            answers_by_source['FarsNet'] = self.farsnet.get_synonyms(question_text, question.length)
            answers_by_source['FarsiYar'] = self.farsiyar.get_synonyms(question_text, question.length)
        elif len(question_words) == 2 and len(question_words[0].split()) == 1 and len(question_words[1].split()) == 1:
            farsnet_answers = self.farsnet.get_synonyms(question_words[0], question.length)
            farsiyar_answers = self.farsiyar.get_synonyms(question_words[0], question.length)
            answers_by_source['FarsNet'] = merge_answers(
                farsnet_answers,
                self.farsnet.get_synonyms(question_words[1], question.length)
            )
            answers_by_source['FarsiYar'] = merge_answers(
                farsiyar_answers,
                self.farsiyar.get_synonyms(question_words[1], question.length)
            )
        elif question_text.startswith('مخالف ') or question_text.startswith('متضاد '):
            answers_by_source['FarsNet'] = self.farsnet.get_antonyms(
                self.normalizer.prepare_antonym_question(question_text),
                question.length
            )
        else:
            answers_by_source['es_wikipedia'] = self.wikipedia_corpus.get_answers_from_clue(question_text, question.length)
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
        if len(answers_probability) > 0:
            return True
        return False

    def get_synonyms(self, question, length):
        farsnet_answers = self.farsnet.get_synonyms(question, length)
        farsiyar_answers = self.farsiyar.get_synonyms(question, length)
        question_words = question.split(' و ')
        if len(question_words) == 2:
            for word in question_words:
                farsnet_answers = merge_answers(farsnet_answers, self.farsnet.get_synonyms(word, length))
                farsiyar_answers = merge_answers(farsiyar_answers, self.farsiyar.get_synonyms(word, length))
        if question.startswith('مخالف ') or question.startswith('متضاد '):
            farsnet_answers = merge_answers(
                farsnet_answers,
                self.farsnet.get_antonyms(self.normalizer.prepare_antonym_question(question), length)
            )
        return {
            'FarsNet': farsnet_answers,
            'FarsiYar': farsiyar_answers
        }

    @staticmethod
    def get_probability(answers_by_source, answer):
        p = 0
        for key in answers_by_source:
            if answer in answers_by_source[key]:
                p += answers_by_source[key][answer]
        return p / (len(answers_by_source))

