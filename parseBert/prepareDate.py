import pandas as pd
from hazm import *
import re

DF_PATH = '../evaluation/df_question_answers_final.csv'
normalizer = Normalizer()
tagger = POSTagger(model='../resources/postagger.model')
lemmatizer = Lemmatizer()
chunker = Chunker(model='../resources/chunker.model')


def make_sentence(question, answer):
    question = normalizer.normalize(question)
    answer = normalizer.normalize(answer)
    tokens = word_tokenize(question)
    question_tags = tagger.tag(tokens)
    chunks = tree2brackets(chunker.parse(question_tags))
    try:
        if question_tags[-1][1] == 'V' or (question_tags[-1][1] == 'PUNC' and question_tags[-2][1] == 'V'):
            if 'آن' in tokens or 'آنجا' in tokens:
                if 'آن' in tokens:
                    i = tokens.index('آن')
                elif 'آنجا' in tokens:
                    i = tokens.index('آنجا')
                if 'که' in tokens:
                    sentence = f'{" ".join(tokens)}، {answer}است. '
                elif tokens[0] == 'آن' and tokens[1] != 'را':
                    sentence = f'{" ".join(tokens)}، {answer}است. '
                elif tokens[i+1] in ['چه', 'که']:
                    sentence = f'{" ".join(tokens)}، {answer}است. '
                else:
                    tokens[i] = answer
                    sentence = ' '.join(tokens)
            elif 'آنکه' in tokens or 'آن‌که' in tokens:
                if 'آنکه' in tokens:
                    i = tokens.index('آنکه')
                elif 'آن‌که' in tokens:
                    i = tokens.index('آن‌که')
                tokens[i] = f'{answer}،'
                sentence = ' '.join(tokens)
            elif 'کسی' == tokens[0] and 'که' == tokens[1]:
                tokens.insert(1, 'است')
                tokens.insert(0, answer)
                sentence = ' '.join(tokens)
            elif 'او' in tokens and question_tags[0][1] != 'P' and 'که' not in tokens:
                i = tokens.index('او')
                tokens[i] = answer
                sentence = ' '.join(tokens)
            elif 'این' in tokens:
                i = tokens.index('این')
                tokens[i], tokens[i+1] = tokens[i+1], answer
                sentence = ' '.join(tokens)
            elif 'است' in tokens[-1]:
                ash = [token for token in tokens if token.endswith('ش') and token != lemmatizer.lemmatize(token)]
                if len(ash) > 0 and 'که' not in tokens and tokens[0] != 'آنچه':
                    i = tokens.index(ash[0])
                    tokens[i] = lemmatizer.lemmatize(tokens[i])
                    tokens.insert(i+1, answer)
                    sentence = ' '.join(tokens)
                elif tokens[0] == 'آنچه':
                    tokens[0] = answer
                    sentence = ' '.join(tokens)
                else:
                    tokens.insert(0, f'{answer}،')
                    sentence = ' '.join(tokens)
            elif 'بود' == tokens[-1] or 'بودند' == tokens[-1]:
                tokens.insert(0, answer)
                sentence = ' '.join(tokens)
            elif 'معادل' in tokens:
                tokens.insert(0, answer)
                sentence = f'{" ".join(tokens)}است. '
            elif tokens[-1].startswith('می'):
                if 'را' in tokens or tokens[0] in ['از', 'به', 'با', 'بر', 'در', 'جز'] or 'است' in tokens:
                    tokens.insert(0, answer)
                    sentence = ' '.join(tokens)
                elif re.match(r'^\[[^\]]*NP\]', chunks):
                    sentence = f'{" ".join(tokens)}، {answer} است.'
                elif question_tags[0][1] == 'AJe':
                    tokens.insert(0, answer)
                    sentence = ' '.join(tokens)
                else:
                    sentence = re.sub(r'(\[[^\]]*\])$', f'{answer} ' + r'\g<1>', chunks)
                    sentence = re.sub(r'[A-Za-z\[\]]', '', sentence)
                    sentence = re.sub(r'\s\s', ' ', sentence)
                    sentence = sentence.strip()
                    if not sentence.endswith('.'):
                        sentence = sentence + '.'
                print(question)
                print(answer)
                print(sentence)
            elif 'گویند' in tokens[-1]:
                tokens.insert(len(tokens)-1, answer)
                sentence = ' '.join(tokens)
            elif 'نیست' == tokens[-1]:
                tokens[len(tokens)-1] = 'است.'
                tokens.insert(0, 'مخالف')
                tokens.insert(0, answer)
                sentence = ' '.join(tokens)
            else:
                sentence = f'{" ".join(tokens)}، {answer} است.'
        elif len(tokens) == 1 or (len(tokens) == 3 and tokens[1] == 'و') or tokens[0] == 'در':
            tokens.insert(0, 'معادل')
            tokens.insert(0, answer)
            tokens.insert(len(tokens), 'است.')
            sentence = ' '.join(tokens)
        else:
            tokens.insert(0, answer)
            tokens.insert(len(tokens), 'است.')
            sentence = ' '.join(tokens)

        sentence = normalizer.normalize(sentence)
        sentence = sentence.strip()
        sentence = sentence.replace('_', ' ')
        sentence = sentence.replace('«', '')
        sentence = sentence.replace('»', '')
        if not sentence.endswith('.') and not sentence.endswith('!'):
            sentence = sentence + '.'
        return sentence
    except Exception as e:
        return ""


df = pd.read_csv(DF_PATH, index_col='Unnamed: 0')
# df = df.drop_duplicates()
df_list = df.values.tolist()
sentences = []
answers = []
for question, answer in df_list:
    answers.append(answer)
    sentences.append(make_sentence(question, answer))
# df = pd.DataFrame({'question': sentences, 'answer': answers})
# df.to_csv('unseen_test_sentences.csv')
