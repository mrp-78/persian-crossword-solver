import logging
from colorama import init
from src.crosswordUtils import read_crossword_from_file, print_table
from src.crosswordSolver import CrosswordSolver


def main():
    file_name = input('نام فایل ورودی را وارد کنید:\n')
    logging.basicConfig(
        filename=f"logs/{file_name}.log",
        format="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
        level=logging.INFO
    )
    crossword = read_crossword_from_file(f'./data/{file_name}', True)
    crossword_solver = CrosswordSolver(crossword, True)
    crossword = crossword_solver.solve()
    print_table(crossword)


if __name__ == '__main__':
    init(autoreset=True)
    main()
