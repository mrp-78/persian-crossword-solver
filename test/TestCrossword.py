import unittest
from src.crossword import CrossWord
from src.evaluation import Evaluation


class TestCrossword(unittest.TestCase):
    def run_test(self, file_name: str):
        print(f'# test {file_name}:')
        crossword = CrossWord(f'../data/{file_name}', False, True)
        crossword.solve()
        evaluation = Evaluation(crossword)
        accuracy, precision = evaluation.get_accuracy_and_precision()
        print(f'accuracy = {accuracy}\nprecision = {precision}')
        for question in crossword.questions:
            ans = crossword.get_calculated_answer(question)
            print(ans)
            self.assertEqual(question.answer, ans)
        print()

    def test_crossword_01(self):
        self.run_test('crossword_01.txt')

    def test_crossword_02(self):
        self.run_test('crossword_02.txt')

    def test_crossword_03(self):
        self.run_test('crossword_03.txt')


if __name__ == '__main__':
    unittest.main()
