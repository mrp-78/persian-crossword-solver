from decouple import config
from elasticsearch import Elasticsearch
from src.normalizer import Normalizer
from src.utils import merge_answers


class Dehkhoda:
    def __init__(self):
        self.es = Elasticsearch(config('ES_HOST'))
        self.index_name = config('ES_DEHKHODA_INDEX_NAME')
        self.normalizer = Normalizer()

    def es_query(self, query: str):
        res = self.es.search(index=self.index_name, body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["description"]
                }
            }
        })
        return res['hits']['hits']

    def get_answers_from_clue(self, clue: str, answer_length: int):
        possible_answers = {}
        docs = self.es_query(clue)
        size = len(docs)
        if size > 10:
            size = 10
        for i in range(size):
            doc = docs[i]['_source']['title']
            doc = self.normalizer.normalize(doc)
            doc = self.normalizer.prepare_word_for_table(doc)
            if len(doc) == answer_length:
                possible_answers = merge_answers(possible_answers, {doc: ((5 - i) / 5) * 0.99})
        return possible_answers
