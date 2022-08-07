from suds.client import Client


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
                if sense.value not in synonyms:
                    synonyms.append(sense.value)
        return synonyms
