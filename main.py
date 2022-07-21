from enum import Enum


class Direction(Enum):
    HORIZONTAL = 1
    VERTICAL = 2


class CrossWord:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.questions = []
        self.crossword_table = [[None for j in range(cols)] for i in range(rows)]

    def add_black_block(self, x: int, y: int):
        self.crossword_table[x][y] = '#'

    def print_table(self):
        print('-' * (4 * self.cols + 1))
        for i in range(self.rows):
            for j in range(self.cols):
                value = self.crossword_table[i][j]
                if not value:
                    value = ' '
                if j != self.cols - 1:
                    print('| ' + value, end=' ')
                else:
                    print('| ' + value + ' |')
            print('-' * (4 * self.cols + 1))


class Question:
    def __init__(self, question: str, x: int, y: int, length: int, direction: Direction):
        self.question = question
        self.x = x
        self.y = y
        self.length = length
        self.direction = direction


def main():
    rows, cols = map(int, input('please enter number of rows and columns of crossword: ').split())
    crossword = CrossWord(rows, cols)
    inp = input('enter black blocks with pairs of (x, y) or type "E" for end: \n')
    while inp != 'E':
        x, y = map(int, inp.split())
        crossword.add_black_block(x, y)
        inp = input()
    crossword.print_table()


if __name__ == '__main__':
    main()
