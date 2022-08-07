from colorama import init
from crossword import CrossWord


def main():
    global crossword
    rows = int(input('تعداد سطرهای جدول:\n'))
    cols = int(input('تعداد ستون‌های جدول:\n'))
    crossword = CrossWord(rows, cols)
    crossword.print_table(True)
    crossword.read_blocked_cells()
    crossword.read_questions()
    crossword.solve()


if __name__ == '__main__':
    crossword: CrossWord
    init(autoreset=True)
    main()
