"""SudokuGame maintains state and enforces the rules of the game."""
# The non-yices portions of this code base come from:
#
# http://newcoder.io/gui/
#
# where the license is:
#
# https://creativecommons.org/licenses/by-sa/3.0/deed.en_US
#
# I have modified the code as I saw fit to suit my purposes.
# All changes are recorded in the git commits.
#

from .SudokuLib import Puzzle, SudokuError
from .SudokuSolver import SudokuSolver
from .SudokuGenerator import SudokuGenerator
from .SudokuOptions import Options

class SudokuGame:
    """
    A Sudoku game, in charge of storing the state of the board and checking
    whether the puzzle is completed.
    """
    def __init__(self, board_name):
        self.board_name = board_name
        self.options = Options()
        self.start_puzzle = Puzzle.resource2puzzle(board_name)
        self.game_over = False
        # puzzle extends start_puzzle
        self.puzzle = None
        # the non-0 entries in solution are 0 in puzzle
        self.solution = None
        self.solver = SudokuSolver(self)

    def start(self):
        """start commences a new game."""
        self.game_over = False
        self.puzzle = self.start_puzzle.clone()
        self.solution = None

    def load(self, path):
        """loads the puzzle from the given path."""
        self.start_puzzle = Puzzle.path2puzzle(path)
        self.start()

    def save(self, path):
        """saves the puzzle to the given path."""
        self.puzzle.puzzle2path(path)

    def new(self):
        """start commences a newly generated game."""
        generator = SudokuGenerator(self.options)
        score, puzzle = generator.generate()
        if self.options.debug:
            puzzle.pprint()
            print(f'Difficulty: {score} Target: {self.options.difficulty} Empty: {puzzle.empty_cells}')
        self.start_puzzle = puzzle.clone()
        self.start()
        return (score, self.options.difficulty, puzzle.empty_cells)

    def solve(self):
        """solve uses the SMT solver to solve the current game."""
        self.solution = self.solver.solve()
        return self.solution is not None

    def dispose(self):
        """dispose cleans up the resources in the Yices library."""
        self.solver.dispose()

    def count_solutions(self):
        """count_solutions returns the number of distinct solutions to the current board."""
        return self.solver.count_models(self.options.debug)

    def get_hint(self):
        """returns the easiest hint."""
        return self.solver.get_hint()

    def get_difficulty(self, sofa):
        """returns the difficulty of the puzzle, as is, or -1 if it is not solvable."""
        diff = [0]
        generator = SudokuGenerator(self.options)
        code = generator.solve(self.puzzle, None, diff, sofa)
        if code == 0:
            return diff[0]
        return -1

    def get_metric(self):
        """computes my notion of difficulty (should be a number between 0 and roughly 100)."""
        return self.solver.core_metric()

    def check(self):
        """Do a quick check that the puzzle is still solvable (i.e. we haven't goofed).
        If it is we return (True, None), otherwise we return (False, wrong) where
        wrong is the non None cells in puzzle that disagree with the solution.
        """
        solution = self.solver.solve()
        if solution is not None:
            return (True, None)
        solution = self.solver.solve(self.start_puzzle)
        if solution is None:
            raise SudokuError("The starting puzzle is not solvable!")
        wrong = []
        for row in range(9):
            for col in range(8):
                if self.start_puzzle.get_cell(row, col) is None:
                    current = self.puzzle.get_cell(row, col)
                    if current is not None and current != solution.get_cell(row, col):
                        wrong.append((row, col))
        return (False, wrong)

    def sanity_check(self):
        """this is for debugging, we check that all our data structures make sense."""
        if self.options.debug:
            print(f'puzzle.sanity_check() = {self.puzzle.sanity_check(self.options.debug)}')
            print(f'puzzle.sanity_check_sofa() = {self.puzzle.sanity_check_sofa()}')


    def get_empty_cell_count(self):
        """returns the number of empty cells in the current puzzle."""
        return self.puzzle.empty_cells

    def clear_solution(self):
        """clear_solution resets the solution."""
        self.solution = None

    def cell_selected(self, row, col):
        """the user has selected the cell, so we can print debugging information."""
        if self.options.debug:
            freedom = self.puzzle.freedom_set(row, col)
            if freedom is not None:
                vals = ' '.join([str(x) for x in range(1, 10) if x in freedom])
                print(f'[{row}, {col}]: {vals}')
            print(f'least free: {self.puzzle.least_free()}')

    def least_free(self):
        """returns the least free cell."""
        return self.puzzle.least_free()

    def check_win(self):
        """check_win determines if the current game has been solved."""
        for row in range(9):
            if not self.__check_row(row):
                return False
        for column in range(9):
            if not self.__check_column(column):
                return False
        for row in range(3):
            for column in range(3):
                if not self.__check_square(row, column):
                    return False
        self.game_over = True
        return True

    def __check_block(self, block): # pylint: disable=R0201
        return set(block) == set(range(1, 10))

    def __check_row(self, row):
        return self.__check_block(self.puzzle.get_row(row))

    def __check_column(self, column):
        return self.__check_block(
            [self.puzzle.get_cell(row, column) for row in range(9)]
        )

    def __check_square(self, row, column):
        return self.__check_block(
            [
                self.puzzle.get_cell(r, c)
                for r in range(row * 3, (row + 1) * 3)
                for c in range(column * 3, (column + 1) * 3)
            ]
        )
