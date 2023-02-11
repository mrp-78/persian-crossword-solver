import pandas as pd
from src.normalizer import Normalizer
from src.modules.farsiyar import FarsiYar
from src.utils import merge_answers

TEST_DF_PATH = '../data/dataframe/df_test.csv'

normalizer = Normalizer()

test_df = pd.read_csv(TEST_DF_PATH, index_col="Unnamed: 0")
test_df_question = test_df['question'].to_numpy()
test_df_answers = test_df['answer'].to_numpy()

farsiyar = FarsiYar()

TP = 0
m = 0
l = 0

for i in range(len(test_df_question)):
    try:
        question_text = test_df_question[i]
        answer = test_df_answers[i]

        question_words = question_text.split(' و ')

        if len(question_text.split()) == 1:
            possible_answers = farsiyar.get_synonyms(question_text, len(answer))
        elif len(question_words) == 2 and len(question_words[0].split()) == 1 and len(question_words[1].split()) == 1:
            farsiyar_answers = farsiyar.get_synonyms(question_words[0], len(answer))

            possible_answers = merge_answers(
                farsiyar_answers,
                farsiyar.get_synonyms(question_words[1], len(answer))
            )
        else:
            continue

        possible_answers = list(possible_answers.keys())
        m += len(possible_answers)
        l += 1
        if answer in possible_answers:
            TP += 1
    except Exception as e:
        print(e)
        break

print('Evaluation Results')
print((TP/l)*100)
print(m/l)
