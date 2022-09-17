import logging
import json
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from decouple import config

es = Elasticsearch(config('ES_HOST'))
es_index = config('ES_INDEX_NAME')
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
                "Id": {
                    "type": "long"
                },
                "InfoBox": {
                    "properties": {
                        "KeysAndValues": {
                            "properties": {
                                "Item1": {
                                    "type": "text",
                                    "analyzer": "parsi"
                                },
                                "Item2": {
                                    "type": "text",
                                    "analyzer": "parsi"
                                }
                            }
                        },
                        "Title": {
                            "type": "text",
                            "analyzer": "parsi"
                        }
                    }
                },
                "IsDisambiguationPage": {
                    "type": "boolean"
                },
                "Links": {
                    "type": "text",
                    "analyzer": "parsi"
                },
                "Namespace": {
                    "type": "long"
                },
                "Rank": {
                    "type": "long"
                },
                "RedirectList": {
                    "type": "text",
                    "analyzer": "parsi"
                },
                "TargetLinksCount": {
                    "type": "long"
                },
                "Text": {
                    "type": "text",
                    "analyzer": "parsi"
                },
                "Title": {
                    "type": "text",
                    "analyzer": "parsi"
                },
                "Type": {
                    "type": "long"
                },
                "Parents": {
                    "type": "text",
                    "analyzer": "parsi"
                }
            }
        }
    })

logging.info("starting to index documents ...")

with open('data/fawiki-20181001-pages-articles-multistream 870508 - 1160676.json') as f:
    i = 0
    actions = []
    while True:
        i += 1
        if i % 1000 == 0:
            helpers.bulk(es, actions)
            actions = []
        line = f.readline()
        if not line or line is None:
            break
        try:
            json_array = json.loads(line)
        except Exception as e:
            logging.error(e)
            logging.error(line)
        actions.append({"_index": es_index, "_source": json_array})

    if i % 1000 != 0:
        helpers.bulk(es, actions)

logging.info("documents was indexed successfully!")
