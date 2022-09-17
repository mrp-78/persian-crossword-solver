import re
from src.enums import Direction
from src.question import Question
from colorama import Fore, Back, Style
from src.crossword import CrossWord


def read_crossword_from_file(file_name: str, read_answers=False):
    crossword = CrossWord(file_name)
    with open(file_name, encoding='utf-8') as f:
        crossword.rows, crossword.cols = map(int, f.readline().split())
        crossword.crossword_table = [[None for j in range(crossword.cols)] for i in range(crossword.rows)]
        blocks = f.readline()
        for i in range(len(blocks)):
            if blocks[i] == '1':
                crossword.black_blocks += 1
                crossword.crossword_table[i // crossword.cols][i % crossword.cols] = '#'
        questions_list = re.split(r'([&#@])', f.readline())
        answers_list = False
        if read_answers:
            answers_list = re.split(r'([&#@])', f.readline())
        read_questions(crossword, questions_list, answers_list)
        calculate_questions_intersects(crossword)
    return crossword


def remove_special_chars_from_list(questions_list: []):
    for q in questions_list:
        if re.match(r'[&#@\-\n]', q) or q == '':
            continue
        yield q


def read_questions(crossword: CrossWord, questions_list: [], answers_list):
    all_questions = remove_special_chars_from_list(questions_list)
    if answers_list:
        all_answers = remove_special_chars_from_list(answers_list)
    question_number = 1
    direction = Direction.HORIZONTAL
    for i in range(crossword.rows):
        x = i
        y = 0
        for j in range(crossword.cols):
            while j < crossword.cols and crossword.crossword_table[i][j] != '#':
                j += 1
            if j - y < 2:
                y = j + 1
                continue
            ans = ''
            if answers_list:
                ans = next(all_answers)
            question = Question(question_number, next(all_questions), x, y, j - y, direction, ans)
            question_number += 1
            crossword.questions.append(question)
            y = j + 1
    direction = Direction.VERTICAL
    for j in range(crossword.cols):
        x = 0
        y = j
        for i in range(crossword.rows):
            while i < crossword.rows and crossword.crossword_table[i][j] != '#':
                i += 1
            if i - x < 2:
                x = i + 1
                continue
            ans = ''
            if answers_list:
                ans = next(all_answers)
            question = Question(question_number, next(all_questions), x, y, i - x, direction, ans)
            question_number += 1
            crossword.questions.append(question)
            x = i + 1


def calculate_questions_intersects(crossword: CrossWord):
    for q1 in crossword.questions:
        for q2 in crossword.questions:
            if q1.direction != q2.direction:
                if q1.direction == Direction.HORIZONTAL:
                    if q2.x <= q1.x <= q2.x + q2.length and q1.y <= q2.y <= q1.y + q1.length:
                        q1.intersect_questions.append(q2)
                else:
                    if q1.x <= q2.x <= q1.x + q1.length and q2.y <= q1.y <= q2.y + q2.length:
                        q1.intersect_questions.append(q2)


def print_table(crossword: CrossWord, is_empty: bool = False):
    for j in range(crossword.cols - 1, -1, -1):
        print(f'  {j + 1} ', end='')
    print()
    if not is_empty:
        print(' ', end='')
    print(Style.BRIGHT + Back.BLACK + Fore.LIGHTWHITE_EX + "-" * (4 * crossword.cols + 1))
    start_col, end_col, step = 0, crossword.cols, 1
    if is_empty:
        start_col, end_col, step = crossword.cols - 1, -1, -1
    for i in range(crossword.rows):
        if not is_empty:
            print(f' {i + 1} ', end='')
        for j in range(start_col, end_col, step):
            value = crossword.crossword_table[i][j]
            if not value:
                value = ' '
            if value == '#':
                print(Style.BRIGHT + Back.BLACK + Fore.LIGHTWHITE_EX + '|', end='')
                print(Style.BRIGHT + Back.LIGHTWHITE_EX + Fore.LIGHTWHITE_EX + f' {value} ', end='')
            else:
                if crossword.evaluation_table is not None and crossword.evaluation_table[i][j] is not None:
                    print(Style.BRIGHT + Back.BLACK + Fore.LIGHTWHITE_EX + '|', end='')
                    if crossword.evaluation_table[i][j]:
                        print(Style.BRIGHT + Back.GREEN + Fore.LIGHTWHITE_EX + f' {value} ', end='')
                    else:
                        print(Style.BRIGHT + Back.RED + Fore.LIGHTWHITE_EX + f' {value} ', end='')
                else:
                    print(Style.BRIGHT + Back.BLACK + Fore.LIGHTWHITE_EX + f'| {value} ', end='')
        print(Style.BRIGHT + Back.BLACK + Fore.LIGHTWHITE_EX + '|', end='')
        if is_empty:
            print(f' {i + 1} ', end='')
        print()
        if not is_empty:
            print(' ', end='')
        print(Style.BRIGHT + Back.BLACK + Fore.LIGHTWHITE_EX + '-' * (4 * crossword.cols + 1))


def get_calculated_answer(crossword: CrossWord, question: Question):
    if question.predicted_answer:
        return question.predicted_answer
    ans = ''
    vx = 0
    vy = 0
    if question.direction == Direction.HORIZONTAL:
        vy = 1
    else:
        vx = 1
    for x in range(question.length):
        ch = crossword.crossword_table[question.x + vx * x][question.y + vy * x]
        if ch is not None:
            ans += ch
        else:
            ans += ' '
    question.predicted_answer = ans
    return ans


def fill_answer_in_table(crossword: CrossWord, answer: str):
    question = crossword.questions[crossword.current_question]
    if len(answer) != question.length:
        return False, 0
    conflicted_blocks = 0
    x = question.x
    y = question.y
    if question.direction == Direction.HORIZONTAL:
        for i in range(len(answer)):
            if crossword.crossword_table[x][y + i]:
                if crossword.crossword_table[x][y + i] != answer[i]:
                    return False, 0
                else:
                    conflicted_blocks += 1
                    continue
            crossword.crossword_table[x][y + i] = answer[i]
    else:
        for i in range(len(answer)):
            if crossword.crossword_table[x + i][y]:
                if crossword.crossword_table[x + i][y] != answer[i]:
                    return False, 0
                else:
                    conflicted_blocks += 1
                    continue
            crossword.crossword_table[x + i][y] = answer[i]
    return crossword, conflicted_blocks
