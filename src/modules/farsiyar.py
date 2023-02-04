import logging
import requests
from decouple import config
from src.normalizer import Normalizer


class FarsiYar:
    def __init__(self):
        self.api_key = config('FARIYAR_API_KEY')
        self.api_url = 'https://api.text-mining.ir'
        self.login_token = self.get_login_token()
        self.normalizer = Normalizer()

    def get_login_token(self):
        url = f'{self.api_url}/api/Token/GetToken?apikey={self.api_key}'
        res = requests.get(url).json()
        return res['token']

    def get_similar_words(self, word: str):
        url = f'{self.api_url}/api/TextSimilarity/GetMostSimilarWord'
        body = {
            'Word': word,
            'TopN': 10
        }
        retry = 0
        while retry < 3:
            try:
                res = requests.post(url, json=body, headers={'Authorization': f'Bearer {self.login_token}'}).json()
                return res
            except Exception as e:
                logging.error(e)
                retry += 1

    def extract_synonyms(self, word: str):
        url = f'{self.api_url}/api/TextSimilarity/ExtractSynonyms'
        retry = 0
        while retry < 3:
            try:
                res = requests.post(url, json=word, headers={'Authorization': f'Bearer {self.login_token}'}).json()
                return res
            except Exception as e:
                logging.error(e)
                retry += 1

    def get_synonyms(self, keyword: str, length: int):
        synonyms = {}
        if len(keyword) == length:
            synonyms[keyword] = 0.6
        syn = self.extract_synonyms(keyword)
        for word in syn:
            value = self.normalizer.normalize(word)
            value = self.normalizer.prepare_word_for_table(value)
            if value not in synonyms and len(value) == length:
                synonyms[value] = 0.6
        similar_words = self.get_similar_words(keyword)
        for word in similar_words:
            value = self.normalizer.normalize(word)
            value = self.normalizer.prepare_word_for_table(value)
            if value not in synonyms and len(value) == length:
                synonyms[value] = 0.6
            syn = self.extract_synonyms(value)
            for w in syn:
                value = self.normalizer.normalize(w)
                value = self.normalizer.prepare_word_for_table(value)
                if value not in synonyms and len(value) == length:
                    synonyms[value] = 0.6
        return synonyms
