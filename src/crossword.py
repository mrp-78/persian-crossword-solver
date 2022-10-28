class CrossWord:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.questions = {}
        self.past_questions = []
        self.forward_questions = []
        self.crossword_table = [[]]
        self.rows = 0
        self.cols = 0
        self.black_blocks = 0
        self.score = 0
        self.filled_questions = 0
        self.conflicted_blocks = 0
        self.sop = 0
        self.heuristic = 0
        self.evaluation_table = None

    def __lt__(self, other):
        return self.score > other.score
