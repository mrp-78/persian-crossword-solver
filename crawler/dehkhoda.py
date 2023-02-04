import requests
import bs4
from hazm import Normalizer
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from decouple import config


class DehkhodaCrawler:
    def __init__(self):
        self.normalizer = Normalizer()
        self.es = Elasticsearch(config('ES_HOST'))
        self.es_index = config('ES_DEHKHODA_INDEX_NAME')
        self.create_es_index()
        self.base_url = 'https://dehkhoda.ut.ac.ir/fa/dictionary/'
        self.from_page = 11000
        self.to_page = 11445
        self.per_page = 30
        self.actions = []

    def create_es_index(self):
        if not self.es.indices.exists(index=self.es_index):
            self.es.indices.create(index=self.es_index, body={
                "mappings": {
                    "properties": {
                        "title": {
                            "type": "text",
                            "analyzer": "parsi"
                        },
                        "description": {
                            "type": "text",
                            "analyzer": "parsi"
                        },
                    }
                }
            })

    def crawl(self):
        for page in range(self.from_page, self.to_page):
            print(page)
            url = f'{self.base_url}?page={page+1}&per-page={self.per_page}'
            try:
                r = requests.get(url)
                bs = bs4.BeautifulSoup(r.text, 'html.parser')
                links = bs.find_all('a')
                for link in links:
                    href = link.get('href')
                    if href is not None and href.startswith(self.base_url):
                        self.crawl_page(href)
            except Exception as e:
                print(e)
        if len(self.actions) > 0:
            helpers.bulk(self.es, self.actions)

    def crawl_page(self, url):
        try:
            r = requests.get(url)
            bs = bs4.BeautifulSoup(r.text, 'html.parser')
            title = bs.find('h1').text
            description = bs.find("div", {"class": "content"}).text
            description = self.normalizer.normalize(description)
            self.add_to_es(title, description)
        except Exception as e:
            print(e)

    def add_to_es(self, title, description):
        if len(self.actions) % 100 == 0:
            helpers.bulk(self.es, self.actions)
            self.actions = []
        self.actions.append({"_index": self.es_index, "_source": {
            'title': title, 'description': description
        }})


if __name__ == '__main__':
    crawler = DehkhodaCrawler()
    crawler.crawl()
