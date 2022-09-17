import logging
from colorama import init
from src.crossword import CrossWord


def main():
    global crossword
    file_name = input('نام فایل ورودی را وارد کنید:\n')
    logging.basicConfig(
        filename=f"logs/{file_name}.log",
        format="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
        level=logging.INFO
    )
    crossword = CrossWord(f'./data/{file_name}')
    crossword.solve()
    crossword.print_table()


if __name__ == '__main__':
    crossword: CrossWord
    init(autoreset=True)
    main()
