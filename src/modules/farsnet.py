import logging
from suds.client import Client
from decouple import config
from src.normalizer import Normalizer


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

    def get_senses_by_synset(self, synset_id: int):
        retry = 0
        while retry < 3:
            try:
                senses = self.sense_service.service.getSensesBySynset(self.api_key, synset_id)
                return senses
            except Exception as e:
                logging.error(e)
                retry += 1

    def get_synonyms(self, keyword: str, length: int):
        synonyms = {}
        if len(keyword) == length:
            synonyms[keyword] = 0.9
        synsets = self.get_synsets_by_word(keyword)
        for synset in synsets:
            senses = self.get_senses_by_synset(synset.id)
            for sense in senses:
                value = self.normalizer.normalize(sense.value)
                value = self.normalizer.prepare_word_for_table(value)
                if value not in synonyms and len(value) == length:
                    synonyms[value] = 0.9
        return synonyms

    def get_antonyms(self, keyword: str, length: int):
        antonyms = {}
        synsets = self.get_synsets_by_word(keyword)
        for synset in synsets:
            antonym_sets = self.synset_service.service.getSynsetRelationsByType(self.api_key, synset.id, ['Antonym'])
            for synset in antonym_sets:
                senses = self.get_senses_by_synset(synset.synsetId2)
                for sense in senses:
                    value = self.normalizer.normalize(sense.value)
                    value = self.normalizer.prepare_word_for_table(value)
                    if value not in antonyms and len(value) == length:
                        antonyms[value] = 0.9
        return antonyms
