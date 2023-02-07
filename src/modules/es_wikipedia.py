from decouple import config
from elasticsearch import Elasticsearch
from src.normalizer import Normalizer
from src.utils import merge_answers


class WikipediaCorpus:
    def __init__(self):
        self.es = Elasticsearch(config('ES_HOST'))
        self.index_name = config('ES_WIKIPEDIA_INDEX_NAME')
        self.normalizer = Normalizer()

    def es_query(self, query: str):
        res = self.es.search(index=self.index_name, body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["*"]
                }
            }
        })
        return res['hits']['hits']

    def get_answers_from_clue(self, clue: str, answer_length: int):
        possible_answers = {}
        docs = self.es_query(clue)
        size = len(docs)
        if size > 3:
            size = 3
        for i in range(size):
            doc = docs[i]['_source']
            score = docs[i]['_score'] / 100
            possible_answers = merge_answers(
                possible_answers,
                self.get_answers_from_string(doc['Title'], answer_length, score * 0.99)
            )
            list_items = ['RedirectList', 'Links']
            for key in list_items:
                for phrase in doc[key]:
                    possible_answers = merge_answers(
                        possible_answers,
                        self.get_answers_from_string(phrase, answer_length, score * 0.9)
                    )
            # for phrase in doc['Parents']:
            #     possible_answers = merge_answers(
            #         possible_answers,
            #         self.get_answers_from_string(phrase, answer_length, score * 0.85)
            #     )
        return possible_answers

    def get_answers_from_string(self, phrase: str, answer_length: int, score: int):
        answers = {}
        normal_phrase = self.normalizer.normalize(phrase)
        prepared_word = self.normalizer.prepare_word_for_table(normal_phrase)
        if len(prepared_word) == answer_length:
            answers[prepared_word] = score
        words = normal_phrase.split()
        if 1 < len(words) < 4:
            for word in words:
                normal_word = self.normalizer.normalize(word)
                normal_word = self.normalizer.prepare_word_for_table(normal_word)
                if len(normal_word) == answer_length:
                    answers[normal_word] = score
        return answers
