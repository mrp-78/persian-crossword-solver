from hazm import Normalizer as Hazm
from src.utils import multiple_replace


class Normalizer:
    def __init__(self):
        self.normalizer = Hazm()

    def normalize(self, word):
        dic = {
            'آ': 'ا',
            'إ': 'ا',
            'أ': 'ا',
            'ؤ': 'و',
            'ئ': 'ی',
            'ة': 'ه',
            'ك': 'ک',
            '\u200c': '',
            ' ': '',
        }
        normalized_word = self.normalizer.normalize(word)
        return multiple_replace(dic, normalized_word)
