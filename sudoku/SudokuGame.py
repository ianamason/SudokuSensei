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

from .SudokuBoard import SudokuBoard
from .SudokuSolver import SudokuSolver


class SudokuGame:
    """
    A Sudoku game, in charge of storing the state of the board and checking
    whether the puzzle is completed.
    """
    def __init__(self, board_fp):
        self.board_fp = board_fp
        self.start_puzzle = SudokuBoard(board_fp).board
        self.game_over = False
        # puzzle extends start_puzzle
        self.puzzle = None
        # the non-0 entries in solution are 0 in puzzle
        self.solution = None
        self.solver = SudokuSolver(self)

    def start(self):
        """start commences a new game."""
        self.game_over = False
        self.puzzle = SudokuBoard.new_board()
        self.solution = None
        for i in range(9):
            for j in range(9):
                self.puzzle[i][j] = self.start_puzzle[i][j]

    def solve(self):
        """solve uses the SMT solver to solve the current game."""
        self.solution = self.solver.solve()
        return self.solution is not None

    def dispose(self):
        print('Census:')
        self.solver.dispose()

    def count_solutions(self):
        """count_solutions returns the number of distinct solutions to the current board."""
        return self.solver.count_models()

    def clear_solution(self):
        """clear_solution resets the solution."""
        self.solution = None


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
        return self.__check_block(self.puzzle[row])

    def __check_column(self, column):
        return self.__check_block(
            [self.puzzle[row][column] for row in range(9)]
        )

    def __check_square(self, row, column):
        return self.__check_block(
            [
                self.puzzle[r][c]
                for r in range(row * 3, (row + 1) * 3)
                for c in range(column * 3, (column + 1) * 3)
            ]
        )
