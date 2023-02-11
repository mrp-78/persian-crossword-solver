import pandas as pd
from src.normalizer import Normalizer
from src.modules.es_wikipedia import WikipediaCorpus
TEST_DF_PATH = '../data/dataframe/df_test.csv'

normalizer = Normalizer()

test_df = pd.read_csv(TEST_DF_PATH, index_col="Unnamed: 0")
test_df_question = test_df['question'].to_numpy()
test_df_answers = test_df['answer'].to_numpy()

wikipedia = WikipediaCorpus()

TP = 0
m = 0

for i in range(len(test_df_question)):
    question = test_df_question[i]
    answer = test_df_answers[i]

    possible_answers = wikipedia.get_answers_from_clue(question, len(answer))
    possible_answers = list(possible_answers.keys())
    m += len(possible_answers)
    if answer in possible_answers:
        TP += 1

print('Evaluation Results')
print((TP/len(test_df_question))*100)
print(m/len(test_df_question))
