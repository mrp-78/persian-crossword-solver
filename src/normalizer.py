import re
from hazm import Normalizer as Hazm
from src.utils import multiple_replace


class Normalizer:
    def __init__(self):
        self.normalizer = Hazm()

    def normalize_list(self, word_list):
        new_list = set()
        for word in word_list:
            new_list.add(self.normalize(word))
        return new_list

    def normalize(self, word):
        dic = {
            r'آ': 'ا',
            r'إ': 'ا',
            r'أ': 'ا',
            r'ؤ': 'و',
            r'ئ': 'ی',
            r'ي': 'ی',
            r'ة': 'ه',
            r'ك': 'ک',
            r'_': '‌',
            r'\u200c': '‌',
            r'\((.*?)\)': '',
        }
        normalized_word = self.normalizer.normalize(word)
        normalized_word = multiple_replace(dic, normalized_word)
        normalized_word = self.filter_persian_alphabet_and_spaces(normalized_word)
        return normalized_word

    @staticmethod
    def filter_persian_alphabet_and_spaces(word):
        reg = r'[^\u0621-\u0628\u062A-\u063A\u0641-\u0642\u0644-\u0648\u064E-\u0651\u0655\u067E\u0686\u0698\u06A9\u06AF\u06BE\u06CC‌\s]'
        return re.sub(reg, '', word)

    @staticmethod
    def prepare_word_for_table(word):
        dic = {
            r'\s': '',
            r'‌': '‌',
            r'\((.*?)\)': '',
        }
        return multiple_replace(dic, word)
