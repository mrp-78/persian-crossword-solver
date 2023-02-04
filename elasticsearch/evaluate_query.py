import logging
import re
import random
from os import walk
from src.crossword import CrossWord
from hazm import *

logging.basicConfig(
    filename=f"../logs/evaluation.log",
    format="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
    level=logging.WARNING
)

my_path = '../data'
crossword_files = []
for (dir_path, dir_names, file_names) in walk(my_path):
    crossword_files.extend(file_names)
    break
random.shuffle(crossword_files)

for file_name in crossword_files:
    with open(f'../data/{file_name}', encoding='utf-8') as f:
        rows, cols = map(int, f.readline().split())
        blocks = f.readline()
        questions_list = re.split('(&|#|@)', f.readline())
        answers_list = re.split('(&|#|@)', f.readline())
        all_questions = CrossWord.remove_special_chars_from_list(questions_list)
        all_answers = CrossWord.remove_special_chars_from_list(answers_list)
        num_of_questions = 0
        while True:
            try:
                question = next(all_questions)
                answer = next(all_answers)
            except StopIteration:
                break
            lemmatizer = Lemmatizer()
            if lemmatizer.lemmatize(answer) != answer:
                print(f'{file_name} {answer} {lemmatizer.lemmatize(answer)}')
