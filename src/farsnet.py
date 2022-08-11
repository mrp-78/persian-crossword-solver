import logging
from suds.client import Client
from hazm import Normalizer
from src.utils import multiple_replace
from decouple import config


class FarsNet:
    def __init__(self):
        self.api_key = config('FARSNET_API_KEY')
        self.synset_service = Client('http://farsnet.nlp.sbu.ac.ir/WebAPI/services/SynsetService?WSDL')
        self.sense_service = Client('http://farsnet.nlp.sbu.ac.ir/WebAPI/services/SenseService?WSDL')
        self.normalizer = Normalizer()

    def get_synsets_by_word(self, word: str):
        retry = 0
        while retry < 3:
            try:
                synsets = self.synset_service.service.getSynsetsByWord(self.api_key, 'EXACT', word)
                return synsets
            except Exception as e:
                logging.error(e)
                retry += 1

    def get_senses_by_synset(self, synset):
        retry = 0
        while retry < 3:
            try:
                senses = self.sense_service.service.getSensesBySynset(self.api_key, synset.id)
                return senses
            except Exception as e:
                logging.error(e)
                retry += 1

    def get_synonyms(self, keyword: str):
        synonyms = [keyword]
        synsets = self.get_synsets_by_word(keyword)
        for synset in synsets:
            senses = self.get_senses_by_synset(synset)
            for sense in senses:
                value = self.normalize(sense.value)
                if value not in synonyms:
                    synonyms.append(value)
        return synonyms

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
