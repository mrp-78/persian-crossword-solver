from colorama import init
from src.crossword import CrossWord
from src.farsnet import FarsNet


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
    fn = FarsNet()
    print(fn.get_synonyms('لم'))
    # main()
