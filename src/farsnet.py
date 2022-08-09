from suds.client import Client
from hazm import Normalizer
from src.utils import multiple_replace


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
                value = self.normalize(sense.value)
                if value not in synonyms:
                    synonyms.append(value)
        print(synonyms)
        return synonyms

    def normalize(self, word):
        dic = {
            'آ': 'ا',
            'إ': 'ا',
            'أ': 'ا',
        }
        normalizer = Normalizer()
        normalized_word = normalizer.normalize(word)
        return multiple_replace(dic, normalized_word)
