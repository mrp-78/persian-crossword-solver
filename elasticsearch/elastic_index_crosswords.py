import logging
import os
import re
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from decouple import config

es = Elasticsearch(config('ES_HOST'))
es_index = config('ES_CROSSWORDS_INDEX_NAME')
logging.basicConfig(
    filename=f"../logs/elasticsearch.log",
    format="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
    level=logging.INFO
)

if not es.indices.exists(index=es_index):
    logging.info('creating elasticsearch index ...')
    es.indices.create(index=es_index, body={
        "mappings": {
            "properties": {
                "clue": {
                    "type": "text",
                    "analyzer": "parsi"
                },
                "answer": {
                    "type": "text",
                    "analyzer": "parsi"
                },
            }
        }
    })

logging.info("starting to index documents ...")

DATA_PATH = '../data/train/'
file_names = os.listdir(DATA_PATH)
questions = []
answers = []
for file_name in file_names:
    with open(f'{DATA_PATH}{file_name}', encoding='utf-8') as f:
        crossword_rows, crossword_cols = map(int, f.readline().split())
        blocks = f.readline()
        questions_list = re.split(r'([&#@])', f.readline())
        answers_list = re.split(r'([&#@])', f.readline())
        if len(questions_list) != len(answers_list):
            print(file_name, len(questions_list), len(answers_list))
            continue
        questions += questions_list
        answers += answers_list

filter_list = ['&', '#', '@', '\n', '']
questions = list(filter(lambda x: x not in filter_list, questions))
answers = list(filter(lambda x: x not in filter_list, answers))
df = pd.DataFrame(list(zip(questions, answers)), columns=['clue', 'answer'])
df = df.drop_duplicates()
data = df.to_numpy()

actions = []
for i in range(len(data)):
    if i % 1000 == 0 and i != 0:
        helpers.bulk(es, actions)
        actions = []
    actions.append({"_index": es_index, "_source": {
        "clue": data[i][0],
        "answer": data[i][1]
    }})

if len(actions) > 0:
    helpers.bulk(es, actions)

logging.info("documents was indexed successfully!")
