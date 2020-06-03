"""SudokuBoard is a simple representation of the board."""
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

from SudokuError import SudokuError



class SudokuBoard:
    """
    Sudoku Board representation

    """

    @staticmethod
    def new_board():
        """Creates an empty board, with all entries being 0."""
        board = [0] * 9
        for i in range(9):
            board[i] = [0] * 9
        return board

    def __init__(self, board_fp):
        self.board = self.__create_board(board_fp)

    def __create_board(self, board_fp):  # pylint: disable=R0201

        board = SudokuBoard.new_board()

        if board_fp is None:
            return board

        row = 0
        column = 0

        for line in board_fp:
            line = line.strip()
            if len(line) != 9:
                raise SudokuError(
                    "Each line in the sudoku puzzle must be 9 chars long."
                )

            for char in line:
                if not char.isdigit():
                    raise SudokuError(
                        "Valid characters for a sudoku puzzle must be in 0-9"
                    )
                #not sure why pylint gets confused here; it doesn't complain about
                #the same idiom in bug.py
                board[row][column] = int(char)  # pylint: disable=E1137
                column += 1
            row += 1
            column = 0

            if row == 9:
                break

        if len(board) != 9:
            raise SudokuError("Each sudoku puzzle must be 9 lines long")
        return board
