import pandas as pd
from decouple import config
from elasticsearch import Elasticsearch
from src.normalizer import Normalizer

TEST_DF_PATH = 'df_question_answers_test_raw.csv'

normalizer = Normalizer()

test_df = pd.read_csv(TEST_DF_PATH, index_col="Unnamed: 0")
test_df_question = test_df['question'].to_numpy()
test_df_answers = test_df['answer'].to_numpy()

es = Elasticsearch(config('ES_HOST'))
index_name = config('ES_DEHKHODA_INDEX_NAME')

TP = 0

for i in range(len(test_df_question)):
    question = test_df_question[i]
    answer = test_df_answers[i]

    res = es.search(index=index_name, body={
                "query": {
                    "multi_match": {
                        "query": question,
                        "fields": ["description"]
                    }
                }
            })
    res = res['hits']['hits']

    total = 15 if len(res) > 15 else len(res)
    ans_list = []
    for j in range(total):
        ans = normalizer.normalize(res[j]['_source']['title'])
        ans = normalizer.prepare_word_for_table(ans)
        ans_list.append(ans)
    if answer in ans_list:
        TP += 1

print('Evaluation Results')
print((TP/len(test_df_question))*100)
